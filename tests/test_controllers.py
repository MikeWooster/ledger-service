import json
from http import HTTPStatus

from ledger.accounting import Ledger
from ledger.accounting_types import get_accounting_type, TypeCode


def test_method_not_allowed_for_GET_on_credit_endpoint(clean_session, client):
    response = client.get("ledger/credit")
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED


def test_add_credit_to_account_success(clean_session, client):
    amount = 1000
    account_number = "19201923830"
    response = client.post(
        "ledger/credit",
        data=json.dumps({"creditAmount": amount, "accountNumber": account_number}),
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == HTTPStatus.CREATED
    assert len(Ledger.get_all_entries()) == 1
    ledger_entry = Ledger.get_all_entries()[0]
    assert ledger_entry.account_number == account_number
    assert ledger_entry.amount == 1000
    assert ledger_entry.accounting_type == get_accounting_type(TypeCode.CREDIT)


def test_empty_ledger_response_as_empty_list(clean_session, client):
    response = client.get("/ledger")
    assert response.status_code == HTTPStatus.OK
    assert response.json == []


def test_single_ledger_entry(clean_session, client):
    entry = Ledger.add_entry("12345", 100, TypeCode.DEBIT)
    response = client.get("/ledger")
    assert response.status_code == HTTPStatus.OK
    assert response.json == [str(entry)]


def test_get_account_balance(clean_session, client):
    account_number = "12345"
    Ledger.add_entry(account_number, 2931, TypeCode.CREDIT)
    response = client.get(f"/account/{account_number}/balance")
    assert response.status_code == HTTPStatus.OK
    assert response.json["balance"] == 2931
