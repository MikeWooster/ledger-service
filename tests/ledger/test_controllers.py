from decimal import Decimal
from http import HTTPStatus

from ledger.authorization.models import Token
from ledger.app.accounting import Ledger
from ledger.app.accounting_types import TypeCode, credit_type, debit_type


class MethodNotAllowedTests:
    """Mixin to test for non-allowed HTTP methods."""

    allowed_methods = set()
    endpoint_url = ""
    default_headers = {}
    default_data = {}

    def get_endpoint(self):
        """Return the requested endpoint.

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

    def test_POST_method_not_allowed(self, db_session, client):
        if "POST" not in self.allowed_methods:
            response = client.post(self.get_endpoint(), headers=self.get_headers(), json=self.get_data())
            assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    def test_PUT_method_not_allowed(self, db_session, client):
        if "PUT" not in self.allowed_methods:
            response = client.put(self.get_endpoint(), headers=self.get_headers(), json=self.get_data())
            assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    def test_PATCH_method_not_allowed(self, db_session, client):
        if "PATCH" not in self.allowed_methods:
            response = client.patch(self.get_endpoint(), headers=self.get_headers(), json=self.get_data())
            assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    def test_DELETE_method_not_allowed(self, db_session, client):
        if "DELETE" not in self.allowed_methods:
            response = client.delete(self.get_endpoint(), headers=self.get_headers(), json=self.get_data())
            assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    def test_HEAD_method_not_allowed(self, client):
        if "HEAD" not in self.allowed_methods:
            response = client.head(self.get_endpoint())
            assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    def test_OPTIONS_method_not_allowed(self, client):
        if "OPTIONS" not in self.allowed_methods:
            response = client.options(self.get_endpoint())
            assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED


class TokenAuthenticationTests:
    """Mixin to test for correct authentication on endpoints."""

    endpoint_url = ""
    auth_scheme = "Token"
    method = ""
    default_data = None
    status_code = None

    def _create_valid_token(self):
        token_value = "foo-bar"
        token = Token(access_token=token_value)
        token.save()
        return token_value

    def _get_valid_authorization_header(self):
        token = self._create_valid_token()
        return f"{self.auth_scheme} {token}"

    def _get_headers(self, **headers):
        default_headers = {"Content-Type": "application/json"}
        default_headers.update(headers)
        return default_headers

    def get_data(self):
        return self.default_data

    def test_valid_authorization_header_is_allowed_access(self, db_session, client):
        authorization_header = self._get_valid_authorization_header()
        headers = self._get_headers(Authorization=authorization_header)
        response = client.open(self.endpoint_url, method=self.method, headers=headers, json=self.get_data())
        assert response.status_code == self.status_code

    def test_invalid_authorization_header_gets_401_unauthorized(self, db_session, client):
        authorization_header = "Token does-not-exist"
        headers = self._get_headers(Authorization=authorization_header)
        response = client.open(self.endpoint_url, method=self.method, headers=headers, json=self.get_data())
        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_missing_authorization_header_gets_401_unauthorized(self, db_session, client):
        headers = self._get_headers()
        response = client.open(self.endpoint_url, method=self.method, headers=headers, json=self.get_data())
        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_badly_formed_authorization_header_gets_401_unauthorized(self, db_session, client):
        authorization_header = "does-not-exist"
        headers = self._get_headers(Authorization=authorization_header)
        response = client.open(self.endpoint_url, method=self.method, headers=headers, json=self.get_data())
        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_incorrect_scheme_in_authorization_header_gets_401_unauthorized(self, db_session, client):
        token = self._create_valid_token()
        authorization_header = f"Bearer {token}"
        headers = self._get_headers(Authorization=authorization_header)
        response = client.open(self.endpoint_url, method=self.method, headers=headers, json=self.get_data())
        assert response.status_code == HTTPStatus.UNAUTHORIZED


class TestTokenAuthorizationOnCreditEndpoint(TokenAuthenticationTests):
    endpoint_url = "/ledger/credit"
    default_data = {"creditAmount": "1000.82", "accountNumber": "12340493"}
    method = "POST"
    status_code = HTTPStatus.CREATED


class TestTokenAuthorizationOnDebitEndpoint(TokenAuthenticationTests):
    endpoint_url = "/ledger/debit"
    default_data = {"debitAmount": "1000.82", "accountNumber": "12340493"}
    method = "POST"
    status_code = HTTPStatus.CREATED


class TestTokenAuthorizationOnLedgerEndpoint(TokenAuthenticationTests):
    endpoint_url = "/ledger"
    method = "GET"
    status_code = HTTPStatus.OK


class TestTokenAuthorizationOnBalanceEndpoint(TokenAuthenticationTests):
    endpoint_url = "/account/12390403/balance"
    method = "GET"
    status_code = HTTPStatus.OK


class TestMethodsNotAllowedOnCreditEndpoint(MethodNotAllowedTests):
    allowed_methods = {"POST", "OPTIONS"}
    endpoint_url = "/ledger/credit"
    default_data = {"creditAmount": "1000.82", "accountNumber": "12340493"}


class TestMethodsNotAllowedOnDebitEndpoint(MethodNotAllowedTests):
    allowed_methods = {"POST", "OPTIONS"}
    endpoint_url = "/ledger/debit"
    default_data = {"debitAmount": "1000.82", "accountNumber": "12340493"}


class TestMethodsNotAllowedOnLedgerEndpoint(MethodNotAllowedTests):
    allowed_methods = {"GET", "OPTIONS", "HEAD"}
    endpoint_url = "/ledger"


class TestMethodsNotAllowedOnBalanceEndpoint(MethodNotAllowedTests):
    allowed_methods = {"GET", "OPTIONS", "HEAD"}
    endpoint_url = "/account/12390403/balance"


def test_add_credit_to_account_success(db_session, authorized_client):
    response = authorized_client.post(
        "ledger/credit",
        json={"creditAmount": "1000.81", "accountNumber": "19201923830"},
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json == {"amount": "1000.81", "accountNumber": "19201923830", "accountingType": "Credit"}
    assert len(Ledger.get_all_entries()) == 1
    ledger_entry = Ledger.get_all_entries()[0]
    assert ledger_entry.account_number == "19201923830"
    assert ledger_entry.amount == Decimal("1000.81")
    assert ledger_entry.accounting_type == credit_type


def test_add_credit_without_application_json_header_returns_bad_request(db_session, authorized_client):
    response = authorized_client.post("ledger/credit")
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_add_debit_to_account_success(db_session, authorized_client):
    response = authorized_client.post(
        "ledger/debit",
        json={"debitAmount": "328.18", "accountNumber": "23938293"},
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json == {"amount": "328.18", "accountNumber": "23938293", "accountingType": "Debit"}
    assert len(Ledger.get_all_entries()) == 1
    ledger_entry = Ledger.get_all_entries()[0]
    assert ledger_entry.account_number == "23938293"
    assert ledger_entry.amount == Decimal("328.18")
    assert ledger_entry.accounting_type == debit_type


def test_add_debit_without_application_json_header_returns_bad_request(db_session, authorized_client):
    response = authorized_client.post("ledger/debit")
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_empty_ledger_response_as_empty_list(db_session, authorized_client):
    response = authorized_client.get("/ledger")
    assert response.status_code == HTTPStatus.OK
    assert response.json == []


def test_single_ledger_entry(db_session, authorized_client):
    Ledger.add_entry("89234", Decimal("100.92"), TypeCode.DEBIT)
    response = authorized_client.get("/ledger")
    assert response.status_code == HTTPStatus.OK
    assert response.json == [{"amount": "100.92", "accountNumber": "89234", "accountingType": "Debit"}]


def test_get_account_balance(db_session, authorized_client):
    account_number = "92373"
    Ledger.add_entry(account_number, Decimal("2931.00"), TypeCode.CREDIT)
    response = authorized_client.get(f"/account/{account_number}/balance")
    assert response.status_code == HTTPStatus.OK
    assert response.json["balance"] == "2931.00"
