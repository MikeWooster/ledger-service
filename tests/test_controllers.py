import json
from http import HTTPStatus

from ledger.accounting import Ledger
from ledger.accounting_types import get_accounting_type, TypeCode


class MethodNotAllowedTests:
    allowed_methods = set()
    endpoint_url = ""
    default_headers = {}
    default_data = {}

    def get_endpoint(self):
        """Returns the requested endpoint.

        Method can be overridden for more complicated use cases.
        """
        return self.endpoint_url

    def get_headers(self):
        return self.default_headers

    def get_data(self):
        return self.default_data

    def test_GET_method_not_allowed(self, client):
        if "GET" not in self.allowed_methods:
            response = client.get(self.get_endpoint())
            assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    def test_POST_method_not_allowed(self, client):
        if "POST" not in self.allowed_methods:
            response = client.post(
                self.get_endpoint(),
                headers=self.get_headers(),
                json=self.get_data(),
            )
            assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    def test_PUT_method_not_allowed(self, client):
        if "PUT" not in self.allowed_methods:
            response = client.put(
                self.get_endpoint(),
                headers=self.get_headers(),
                json=self.get_data(),
            )
            assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    def test_PATCH_method_not_allowed(self, client):
        if "PATCH" not in self.allowed_methods:
            response = client.patch(
                self.get_endpoint(),
                headers=self.get_headers(),
                json=self.get_data(),
            )
            assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    def test_DELETE_method_not_allowed(self, client):
        if "DELETE" not in self.allowed_methods:
            response = client.delete(
                self.get_endpoint(),
                headers=self.get_headers(),
                json=self.get_data(),
            )
            assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    def test_HEAD_method_not_allowed(self, client):
        if "HEAD" not in self.allowed_methods:
            response = client.head(self.get_endpoint())
            assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    def test_OPTIONS_method_not_allowed(self, client):
        if "OPTIONS" not in self.allowed_methods:
            response = client.options(self.get_endpoint())
            assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED


class TestMethodsNotAllowedOnCreditEndpoint(MethodNotAllowedTests):
    allowed_methods = {"POST", "OPTIONS"}
    endpoint_url = "/ledger/credit"
    default_data = {"creditAmount": 1000, "accountNumber": "12340493"}


class TestMethodsNotAllowedOnLedgerEndpoint(MethodNotAllowedTests):
    allowed_methods = {"GET", "OPTIONS", "HEAD"}
    endpoint_url = "/ledger"


class TestMethodsNotAllowedOnBalanceEndpoint(MethodNotAllowedTests):
    allowed_methods = {"GET", "OPTIONS", "HEAD"}
    endpoint_url = "/account/12390403/balance"


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
