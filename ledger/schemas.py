from dataclasses import dataclass
from decimal import Decimal

from marshmallow import Schema, fields, post_load


class LedgerEntrySchema(Schema):
    """For serializing a LedgerEntry for responses."""
    accountNumber = fields.Str(
        attribute="account_number",
    )
    accountingType = fields.Str(
        attribute="accounting_type",
    )
    amount = fields.Str(
        attribute="amount",
    )


@dataclass
class TransactionData:
    """Deserialized credit/debit request."""
    amount: Decimal
    account_number: str


class CreditSchema(Schema):
    creditAmount = fields.Decimal(
        attribute="amount",
        required=True,
    )
    accountNumber = fields.Str(
        attribute="account_number",
        required=True,
    )

    @post_load
    def create_credit_data(self, data) -> TransactionData:
        return TransactionData(**data)

    class Meta:
        strict = True


class DebitSchema(Schema):
    debitAmount = fields.Decimal(
        attribute="amount",
        required=True,
    )
    accountNumber = fields.Str(
        attribute="account_number",
        required=True,
    )

    @post_load
    def create_debit_data(self, data) -> TransactionData:
        return TransactionData(**data)

    class Meta:
        strict = True


class BalanceSchema(Schema):
    balance = fields.Str()


ledger_entry_schema = LedgerEntrySchema()
credit_schema = CreditSchema()
debit_schema = DebitSchema()
balance_schema = BalanceSchema()
