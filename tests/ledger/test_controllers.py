from datetime import datetime
from decimal import Decimal
from http import HTTPStatus
from unittest.mock import patch

import pytz
from freezegun import freeze_time

from ledger.app.accounting import Ledger
from ledger.app.accounting_types import TypeCode, credit_type, debit_type
from ledger.authorization.models import Token


def assertDictContains(expected: dict, actual: dict):
    """Assert whether a sub dictionary is part of a larger dictionary."""
    for key in expected:
        assert key in actual
        assert expected[key] == actual[key]


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


class TestTokenAuthorizationOnTransactionHistoryEndpoint(TokenAuthenticationTests):
    endpoint_url = "/account/12390403/transactions"
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


class TestMethodsNotAllowedOnTransactionHistoryEndpoint(MethodNotAllowedTests):
    allowed_methods = {"GET", "OPTIONS", "HEAD"}
    endpoint_url = "/account/12390403/transactions"


class TestMethodsNotAllowedOnBalanceEndpoint(MethodNotAllowedTests):
    allowed_methods = {"GET", "OPTIONS", "HEAD"}
    endpoint_url = "/account/12390403/balance"


class TestCreditView:
    def test_add_credit_to_account_success(self, db_session, authorized_client):
        account_number = "19201923830"
        response = authorized_client.post(
            "ledger/credit",
            json={"creditAmount": "1000.81", "accountNumber": account_number},
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == HTTPStatus.CREATED
        assertDictContains(
            expected={
                "amount": "1000.81",
                "accountNumber": account_number,
                "accountingType": "Credit",
                "balance": "1000.81",
            },
            actual=response.json,
        )

        assert len(Ledger.get_entries_for_account(account_number)) == 1
        ledger_entry = Ledger.get_entries_for_account(account_number)[0]
        assert ledger_entry.account_number == account_number
        assert ledger_entry.amount == Decimal("1000.81")
        assert ledger_entry.accounting_type == credit_type

    def test_add_credit_without_application_json_header_returns_bad_request(
        self, db_session, authorized_client
    ):
        response = authorized_client.post("ledger/credit")
        assert response.status_code == HTTPStatus.BAD_REQUEST

    @patch("ledger.app.accounting.uuid.uuid4")
    def test_add_credit_stores_a_unique_transaction_id(self, mock_uuid4, db_session, authorized_client):
        account_number = "9729399840"
        uuid = "2b391f46-8c68-42e4-8364-ff344f092987"
        mock_uuid4.return_value = uuid
        response = authorized_client.post(
            "ledger/credit",
            json={"creditAmount": "1000.81", "accountNumber": account_number},
            headers={"Content-Type": "application/json"},
        )
        assert response.json["transactionId"] == uuid
        ledger_entry = Ledger.get_entries_for_account(account_number)[0]
        assert ledger_entry.transaction_id == uuid

    def test_add_credit_sets_created_at(self, db_session, authorized_client):
        account_number = "87665765"
        utc_now = datetime(2018, 3, 4, 12, 43, 22, 829_312, tzinfo=pytz.utc)
        with freeze_time(utc_now):
            response = authorized_client.post(
                "ledger/credit",
                json={"creditAmount": "1000.81", "accountNumber": account_number},
                headers={"Content-Type": "application/json"},
            )
        assert response.json["createdAt"] == "2018-03-04T12:43:22.829312+00:00"
        ledger_entry = Ledger.get_entries_for_account(account_number)[0]
        assert ledger_entry.created_at == utc_now


class TestDebitView:
    def test_add_debit_to_account_success(self, db_session, authorized_client):
        account_number = "23938292"
        response = authorized_client.post(
            "ledger/debit",
            json={"debitAmount": "328.18", "accountNumber": account_number},
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == HTTPStatus.CREATED
        assertDictContains(
            expected={
                "amount": "328.18",
                "accountNumber": account_number,
                "accountingType": "Debit",
                "balance": "-328.18",
            },
            actual=response.json,
        )
        assert len(Ledger.get_entries_for_account(account_number)) == 1
        ledger_entry = Ledger.get_entries_for_account(account_number)[0]
        assert ledger_entry.account_number == account_number
        assert ledger_entry.amount == Decimal("328.18")
        assert ledger_entry.accounting_type == debit_type

    def test_add_debit_without_application_json_header_returns_bad_request(
        self, db_session, authorized_client
    ):
        response = authorized_client.post("ledger/debit")
        assert response.status_code == HTTPStatus.BAD_REQUEST

    @patch("ledger.app.accounting.uuid.uuid4")
    def test_add_debit_stores_a_unique_transaction_id(self, mock_uuid4, db_session, authorized_client):
        account_number = "9729399840"
        uuid = "2b391f46-8c68-42e4-8364-ff344f092987"
        mock_uuid4.return_value = uuid
        response = authorized_client.post(
            "ledger/debit",
            json={"debitAmount": "1000.81", "accountNumber": account_number},
            headers={"Content-Type": "application/json"},
        )
        assert response.json["transactionId"] == uuid
        ledger_entry = Ledger.get_entries_for_account(account_number)[0]
        assert ledger_entry.transaction_id == uuid

    def test_add_debit_sets_created_at(self, db_session, authorized_client):
        account_number = "87665765"
        utc_now = datetime(2018, 3, 4, 12, 43, 22, 829_312, tzinfo=pytz.utc)
        with freeze_time(utc_now):
            response = authorized_client.post(
                "ledger/debit",
                json={"debitAmount": "1000.81", "accountNumber": account_number},
                headers={"Content-Type": "application/json"},
            )
        assert response.json["createdAt"] == "2018-03-04T12:43:22.829312+00:00"
        ledger_entry = Ledger.get_entries_for_account(account_number)[0]
        assert ledger_entry.created_at == utc_now


def test_add_debit_without_application_json_header_returns_bad_request(db_session, authorized_client):
    response = authorized_client.post("ledger/debit")
    assert response.status_code == HTTPStatus.BAD_REQUEST


class TestTransactionHistoryView:
    def test_account_holder_does_not_exist_response_as_empty_list(self, db_session, authorized_client):
        account_number = "1234390"
        response = authorized_client.get(f"/account/{account_number}/transactions")
        assert response.status_code == HTTPStatus.OK
        assert response.json == []

    def test_one_valid_entry(self, db_session, authorized_client):
        account_number = "89234"
        Ledger.add_entry(account_number, Decimal("100.92"), TypeCode.DEBIT)
        response = authorized_client.get(f"/account/{account_number}/transactions")
        assert response.status_code == HTTPStatus.OK
        assert len(response.json) == 1
        assertDictContains(
            expected={
                "amount": "100.92",
                "accountNumber": "89234",
                "accountingType": "Debit",
                "balance": "-100.92",
            },
            actual=response.json[0],
        )

    def test_only_account_number_entries_are_returned(self, db_session, authorized_client):
        account_number = "89234"
        Ledger.add_entry(account_number, Decimal("100.92"), TypeCode.DEBIT)
        Ledger.add_entry("923929", Decimal("928.92"), TypeCode.CREDIT)
        response = authorized_client.get(f"/account/{account_number}/transactions")
        assert response.status_code == HTTPStatus.OK
        assert len(response.json) == 1
        assertDictContains(
            expected={
                "amount": "100.92",
                "accountNumber": "89234",
                "accountingType": "Debit",
                "balance": "-100.92",
            },
            actual=response.json[0],
        )

    def test_multiple_entries_populates_balance(self, db_session, authorized_client):
        account_number = "89234"
        Ledger.add_entry(account_number, Decimal("201.74"), TypeCode.CREDIT)
        Ledger.add_entry(account_number, Decimal("100.92"), TypeCode.DEBIT)
        Ledger.add_entry(account_number, Decimal("928.32"), TypeCode.CREDIT)
        response = authorized_client.get(f"/account/{account_number}/transactions")
        assert response.status_code == HTTPStatus.OK
        assert len(response.json) == 3
        # Expecting entry to be in reverse order.
        assertDictContains(
            expected={
                "amount": "928.32",
                "accountNumber": "89234",
                "accountingType": "Credit",
                "balance": "1029.14",
            },
            actual=response.json[0],
        )
        assertDictContains(
            expected={
                "amount": "100.92",
                "accountNumber": "89234",
                "accountingType": "Debit",
                "balance": "100.82",
            },
            actual=response.json[1],
        )
        assertDictContains(
            expected={
                "amount": "201.74",
                "accountNumber": "89234",
                "accountingType": "Credit",
                "balance": "201.74",
            },
            actual=response.json[2],
        )

    def test_multiple_entries_with_limit_filter(self, db_session, authorized_client):
        account_number = "939288202"

        # Create 5 transactions
        Ledger.add_entry(account_number, Decimal("201.74"), TypeCode.CREDIT)
        Ledger.add_entry(account_number, Decimal("100.92"), TypeCode.DEBIT)
        Ledger.add_entry(account_number, Decimal("928.32"), TypeCode.CREDIT)
        Ledger.add_entry(account_number, Decimal("71.21"), TypeCode.DEBIT)
        Ledger.add_entry(account_number, Decimal("93.21"), TypeCode.CREDIT)

        # Limit the transactions to 3
        response = authorized_client.get(f"/account/{account_number}/transactions?limit=3")

        assert response.status_code == HTTPStatus.OK
        assert len(response.json) == 3

        assertDictContains(
            expected={
                "amount": "93.21",
                "accountNumber": "939288202",
                "accountingType": "Credit",
                "balance": "1051.14",
            },
            actual=response.json[0],
        )
        assertDictContains(
            expected={
                "amount": "71.21",
                "accountNumber": "939288202",
                "accountingType": "Debit",
                "balance": "957.93",
            },
            actual=response.json[1],
        )
        assertDictContains(
            expected={
                "amount": "928.32",
                "accountNumber": "939288202",
                "accountingType": "Credit",
                "balance": "1029.14",
            },
            actual=response.json[2],
        )

    def test_with_limit_filter_not_an_integer_returns_bad_request(self, db_session, authorized_client):
        account_number = "939288202"
        response = authorized_client.get(f"/account/{account_number}/transactions?limit=foo")
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert "error" in response.json
        assert "description" in response.json["error"]
        expected_message = "Unrecognized limit parameter: 'foo'"
        assert response.json["error"]["description"] == expected_message

    @patch("ledger.app.accounting.uuid.uuid4")
    def test_transaction_id_is_present_in_transaction_history(
        self, mock_uuid4, db_session, authorized_client
    ):
        mock_uuid4.return_value = "6e7f52e6-4003-4c34-9581-2e52788b2d91"
        account_number = "939288202"

        Ledger.add_entry(account_number, Decimal("201.74"), TypeCode.CREDIT)

        response = authorized_client.get(f"/account/{account_number}/transactions")

        assert response.status_code == HTTPStatus.OK
        assert "transactionId" in response.json[0]
        assert response.json[0]["transactionId"] == "6e7f52e6-4003-4c34-9581-2e52788b2d91"

    def test_each_transaction_has_created_at_set(self, db_session, authorized_client):
        account_number = "939288202"
        transaction_one_time = datetime(2018, 3, 4, 12, 43, 22, 829_312, tzinfo=pytz.utc)
        transaction_two_time = datetime(2018, 4, 5, 12, 23, 12, 243_546, tzinfo=pytz.utc)
        with freeze_time(transaction_one_time):
            Ledger.add_entry(account_number, Decimal("201.74"), TypeCode.CREDIT)
        with freeze_time(transaction_two_time):
            Ledger.add_entry(account_number, Decimal("10.19"), TypeCode.DEBIT)

        response = authorized_client.get(f"/account/{account_number}/transactions")

        assert response.status_code == HTTPStatus.OK
        assertDictContains(
            expected={"createdAt": "2018-04-05T12:23:12.243546+00:00"}, actual=response.json[0]
        )
        assertDictContains(
            expected={"createdAt": "2018-03-04T12:43:22.829312+00:00"}, actual=response.json[1]
        )


class TestAccountBalanceView:
    def test_get_account_balance(self, db_session, authorized_client):
        account_number = "92373"
        Ledger.add_entry(account_number, Decimal("2931.00"), TypeCode.CREDIT)
        response = authorized_client.get(f"/account/{account_number}/balance")
        assert response.status_code == HTTPStatus.OK
        assert response.json["balance"] == "2931.00"
