from functools import wraps
from http import HTTPStatus

from flask import jsonify, request
from flask.views import MethodView
from werkzeug.exceptions import Unauthorized

from ledger.app.exceptions import BadRequest
from ledger.authorization.utils import token_is_valid
from ledger.app.accounting import Balance, Ledger
from ledger.app.accounting_types import TypeCode
from ledger.app.schemas import balance_schema, credit_schema, debit_schema, ledger_entry_schema


def authorization_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        unauthorized_exception = Unauthorized("Authorization header missing or invalid.")
        if "Authorization" not in request.headers:
            raise unauthorized_exception
        try:
            scheme, token = request.headers["Authorization"].split()
        except Exception:
            raise unauthorized_exception
        if scheme.upper() != "TOKEN":
            raise unauthorized_exception
        if not token_is_valid(token):
            raise unauthorized_exception
        return func(*args, **kwargs)

    return decorated_function


class AuthorizedMethodView(MethodView):
    decorators = [authorization_required]


class CreateLedgerEntryView(AuthorizedMethodView):
    schema = None
    type_code = None

    def post(self):
        post_data = self.get_json_from_request()
        result = self.schema.load(post_data).data

        entry = Ledger.add_entry(
            account_number=result.account_number, amount=result.amount, type_code=self.type_code
        )
        serialized_entry = ledger_entry_schema.dump(entry)
        return jsonify(serialized_entry.data), HTTPStatus.CREATED

    def get_json_from_request(self):
        post_data = request.get_json()
        if post_data is None:
            raise BadRequest()
        return post_data


class CreditView(CreateLedgerEntryView):
    """Add a credit amount to the ledger."""

    schema = credit_schema
    type_code = TypeCode.CREDIT


class DebitView(CreateLedgerEntryView):
    """Add a debit amount to the ledger."""

    schema = debit_schema
    type_code = TypeCode.DEBIT


class TransactionHistoryView(AuthorizedMethodView):
    """View the ledger."""

    def get(self, account_number: str):
        if self._limit_is_provided():
            entries = Ledger.get_entries_for_account_with_limit(account_number, request.args["limit"])
        else:
            entries = Ledger.get_entries_for_account(account_number)
        response = self._build_response_from_entries(entries)
        return jsonify(response), HTTPStatus.OK

    def _limit_is_provided(self):
        if "limit" not in request.args:
            return False
        limit_parameter = request.args["limit"]
        try:
            int(limit_parameter)
        except Exception:
            raise BadRequest(f"Unrecognized limit parameter: '{limit_parameter}'")
        return True

    @staticmethod
    def _build_response_from_entries(entries):
        response = []
        for entry in entries:
            serialized_entry = ledger_entry_schema.dump(entry)
            response.append(serialized_entry.data)
        return response


class AccountBalanceView(AuthorizedMethodView):
    """Get the account balance for an account."""

    def get(self, account_number: str):
        balance = Balance.get_for_account(account_number)
        serialized_entry = balance_schema.dump({"balance": balance})
        return jsonify(serialized_entry.data), HTTPStatus.OK
