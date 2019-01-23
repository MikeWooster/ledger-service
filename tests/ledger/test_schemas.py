from datetime import datetime
from decimal import Decimal
from uuid import UUID

import pytest
from marshmallow import ValidationError

from ledger.app.accounting import LedgerEntry
from ledger.app.accounting_types import credit_type, debit_type
from ledger.app.schemas import credit_schema, ledger_entry_schema, debit_schema, balance_schema


class TestLedgerEntrySchema:
    schema = ledger_entry_schema

    def test_serializing_object_with_valid_credit_type(self):
        created_timestamp = datetime(2018, 1, 1)
        transaction_id = UUID("07831682-8a29-4176-a50d-8e69b9c5c5db")
        ledger_entry = LedgerEntry(
            account_number="12345678",
            accounting_type=credit_type,
            amount=Decimal("1283.92"),
            created_at=created_timestamp,
            transaction_id=transaction_id,
            balance=Decimal("-20.00"),
        )
        serialized_data = self.schema.dump(ledger_entry).data
        assert serialized_data["accountNumber"] == "12345678"
        assert serialized_data["accountingType"] == "Credit"
        assert serialized_data["amount"] == "1283.92"
        assert serialized_data["createdAt"] == "2018-01-01T00:00:00+00:00"
        assert serialized_data["transactionId"] == "07831682-8a29-4176-a50d-8e69b9c5c5db"
        assert serialized_data["balance"] == "-20.00"

    def test_serializing_object_with_valid_debit_type(self):
        created_timestamp = datetime(2016, 4, 4)
        transaction_id = UUID("d6aa3369-08af-47be-aba3-d1969c0df138")
        ledger_entry = LedgerEntry(
            account_number="399383902",
            accounting_type=debit_type,
            amount=Decimal("827.81"),
            created_at=created_timestamp,
            transaction_id=transaction_id,
            balance=Decimal("190.00"),
        )
        serialized_data = self.schema.dump(ledger_entry).data
        assert serialized_data["accountNumber"] == "399383902"
        assert serialized_data["accountingType"] == "Debit"
        assert serialized_data["amount"] == "827.81"
        assert serialized_data["createdAt"] == "2016-04-04T00:00:00+00:00"
        assert serialized_data["transactionId"] == "d6aa3369-08af-47be-aba3-d1969c0df138"
        assert serialized_data["balance"] == "190.00"


class TestCreditSchema:
    schema = credit_schema

    def test_deserializing_object_with_valid_data(self):
        data = {"creditAmount": "120.32", "accountNumber": "93929393"}
        result = self.schema.load(data).data
        assert result.amount == Decimal("120.32")
        assert result.account_number == "93929393"

    def test_missing_account_number_raises_validation_error(self):
        data = {"creditAmount": "383.20"}
        with pytest.raises(ValidationError) as exc_info:
            self.schema.load(data)
        assert "accountNumber" in exc_info.value.messages
        assert "Missing data for required field." in exc_info.value.messages["accountNumber"]

    def test_missing_credit_amount_raises_validation_error(self):
        data = {"accountNumber": "93929393"}
        with pytest.raises(ValidationError) as exc_info:
            self.schema.load(data)
        assert "creditAmount" in exc_info.value.messages
        assert "Missing data for required field." in exc_info.value.messages["creditAmount"]

    def test_missing_all_fields_raises_validation_error(self):
        data = {}
        with pytest.raises(ValidationError) as exc_info:
            self.schema.load(data)
        assert "accountNumber" in exc_info.value.messages
        assert "Missing data for required field." in exc_info.value.messages["accountNumber"]
        assert "creditAmount" in exc_info.value.messages
        assert "Missing data for required field." in exc_info.value.messages["creditAmount"]

    def test_additional_fields_are_ignored(self):
        data = {"creditAmount": "120.32", "accountNumber": "93929393", "additionalField": "value"}
        result = self.schema.load(data).data
        assert result.amount == Decimal("120.32")
        assert result.account_number == "93929393"


class TestDebitSchema:
    schema = debit_schema

    def test_deserializing_object_with_valid_data(self):
        data = {"debitAmount": "120.32", "accountNumber": "93929393"}
        result = self.schema.load(data).data
        assert result.amount == Decimal("120.32")
        assert result.account_number == "93929393"

    def test_missing_account_number_raises_validation_error(self):
        data = {"debitAmount": "383.20"}
        with pytest.raises(ValidationError) as exc_info:
            self.schema.load(data)
        assert "accountNumber" in exc_info.value.messages
        assert "Missing data for required field." in exc_info.value.messages["accountNumber"]

    def test_missing_debit_amount_raises_validation_error(self):
        data = {"accountNumber": "93929393"}
        with pytest.raises(ValidationError) as exc_info:
            self.schema.load(data)
        assert "debitAmount" in exc_info.value.messages
        assert "Missing data for required field." in exc_info.value.messages["debitAmount"]

    def test_missing_all_fields_raises_validation_error(self):
        data = {}
        with pytest.raises(ValidationError) as exc_info:
            self.schema.load(data)
        assert "accountNumber" in exc_info.value.messages
        assert "Missing data for required field." in exc_info.value.messages["accountNumber"]
        assert "debitAmount" in exc_info.value.messages
        assert "Missing data for required field." in exc_info.value.messages["debitAmount"]

    def test_additional_fields_are_ignored(self):
        data = {"debitAmount": "120.32", "accountNumber": "93929393", "additionalField": "value"}
        result = self.schema.load(data).data
        assert result.amount == Decimal("120.32")
        assert result.account_number == "93929393"


class TestBalanceSchema:
    schema = balance_schema

    def test_serializing_object_with_valid_balance(self):
        balance = Decimal("8382.29")
        result = self.schema.dump({"balance": balance}).data
        assert result["balance"] == "8382.29"
