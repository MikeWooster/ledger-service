from decimal import Decimal
from typing import NamedTuple

from marshmallow import Schema, fields, post_load


class LedgerEntrySchema(Schema):
    """For serializing a LedgerEntry for responses."""

    accountNumber = fields.Str(attribute="account_number")
    accountingType = fields.Str(attribute="accounting_type")
    amount = fields.Str(attribute="amount")


class TransactionData(NamedTuple):
    """Deserialized credit/debit request."""

    amount: Decimal
    account_number: str


class CreditSchema(Schema):
    """Deserializer for a credit request."""

    creditAmount = fields.Decimal(attribute="amount", required=True)
    accountNumber = fields.Str(attribute="account_number", required=True)

    @post_load
    def create_credit_data(self, data) -> TransactionData:
        return TransactionData(**data)

    class Meta:
        strict = True


class DebitSchema(Schema):
    """Deserializer for a debit request."""

    debitAmount = fields.Decimal(attribute="amount", required=True)
    accountNumber = fields.Str(attribute="account_number", required=True)

    @post_load
    def create_debit_data(self, data) -> TransactionData:
        return TransactionData(**data)

    class Meta:
        strict = True


class BalanceSchema(Schema):
    """Serializer for balance responses."""

    balance = fields.Str()


ledger_entry_schema = LedgerEntrySchema()
credit_schema = CreditSchema()
debit_schema = DebitSchema()
balance_schema = BalanceSchema()
