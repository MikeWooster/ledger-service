from http import HTTPStatus

from flask import jsonify, request
from flask.views import MethodView

from ledger.accounting import Balance, Ledger
from ledger.accounting_types import TypeCode
from ledger.schemas import balance_schema, credit_schema, debit_schema, ledger_entry_schema


class Credit(MethodView):
    """Add a credit amount to the ledger."""

    def post(self):
        post_data = request.get_json()
        result = credit_schema.load(post_data).data

        entry = Ledger.add_entry(result.account_number, result.amount, TypeCode.CREDIT)
        serialized_entry = ledger_entry_schema.dump(entry)
        return jsonify(serialized_entry.data), HTTPStatus.CREATED


class Debit(MethodView):
    """Add a debit amount to the ledger."""

    def post(self):
        post_data = request.get_json()
        result = debit_schema.load(post_data).data

        entry = Ledger.add_entry(
            account_number=result.account_number, amount=result.amount, type_code=TypeCode.DEBIT
        )
        serialized_entry = ledger_entry_schema.dump(entry)
        return jsonify(serialized_entry.data), HTTPStatus.CREATED


class LedgerView(MethodView):
    """View the ledger."""

    def get(self):
        entries = Ledger.get_all_entries()
        response = []
        for entry in entries:
            serialized_entry = ledger_entry_schema.dump(entry)
            response.append(serialized_entry.data)
        return jsonify(response), HTTPStatus.OK


class AccountBalance(MethodView):
    """Get the account balance for an account."""

    def get(self, account_number):
        balance = Balance.get_for_account(account_number)
        serialized_entry = balance_schema.dump({"balance": balance})
        return jsonify(serialized_entry.data), HTTPStatus.OK
