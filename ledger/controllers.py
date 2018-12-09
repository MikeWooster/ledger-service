from http import HTTPStatus

from flask import Blueprint, jsonify, request

from ledger.accounting import Balance, Ledger
from ledger.accounting_types import TypeCode
from ledger.schemas import credit_schema, ledger_entry_schema, debit_schema, balance_schema


blueprint = Blueprint("ledger", __name__, url_prefix="/")


@blueprint.route("/ledger/credit", methods=("POST",))
def credit():
    if request.method == "POST":
        post_data = request.get_json()
        result = credit_schema.load(post_data).data

        entry = Ledger.add_entry(result.account_number, result.amount, TypeCode.CREDIT)
        serialized_entry = ledger_entry_schema.dump(entry)
        return jsonify(serialized_entry.data), HTTPStatus.CREATED


@blueprint.route("/ledger/debit", methods=("POST",))
def debit():
    if request.method == "POST":
        post_data = request.get_json()
        result = debit_schema.load(post_data).data

        entry = Ledger.add_entry(
            account_number=result.account_number, amount=result.amount, type_code=TypeCode.DEBIT
        )
        serialized_entry = ledger_entry_schema.dump(entry)
        return jsonify(serialized_entry.data), HTTPStatus.CREATED


@blueprint.route("/ledger", methods=("GET",))
def ledger():
    if request.method == "GET":
        entries = Ledger.get_all_entries()
        response = []
        for entry in entries:
            serialized_entry = ledger_entry_schema.dump(entry)
            response.append(serialized_entry.data)
        return jsonify(response), HTTPStatus.OK


@blueprint.route("/account/<account_number>/balance", methods=("GET",))
def account_balance(account_number):
    if request.method == "GET":
        balance = Balance.get_for_account(account_number)
        serialized_entry = balance_schema.dump({"balance": balance})
        return jsonify(serialized_entry.data), HTTPStatus.OK
