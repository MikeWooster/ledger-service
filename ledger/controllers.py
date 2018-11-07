from http import HTTPStatus

from flask import Blueprint, request, jsonify

from ledger.accounting import Balance, Ledger
from ledger.accounting_types import TypeCode


blueprint = Blueprint("ledger",  __name__, url_prefix="/")


@blueprint.route("/ledger/credit", methods=("POST",))
def credit():
    if request.method == "POST":
        post_data = request.get_json()
        credit_amount = post_data['creditAmount']
        account_number = post_data['accountNumber']

        entry = Ledger.add_entry(account_number, credit_amount, TypeCode.CREDIT)
        return str(entry), HTTPStatus.CREATED


@blueprint.route("/ledger", methods=("GET",))
def ledger():
    if request.method == "GET":
        entries = Ledger.get_all_entries()
        return jsonify([str(entry) for entry in entries])


@blueprint.route("/account/<account_number>/balance", methods=("GET",))
def account_balance(account_number):
    if request.method == "GET":
        balance = Balance.get_for_account(account_number)
        return jsonify({"balance": balance})
