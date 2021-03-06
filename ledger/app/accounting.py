import uuid
from datetime import datetime
from decimal import Decimal
from typing import List

import pytz
from sqlalchemy.orm import Query
from sqlalchemy.orm.exc import NoResultFound

from ledger.app import models
from ledger.app.accounting_types import AbstractEntryType, TypeCode, get_accounting_type


class LedgerEntry:
    """Representation of an entry in the Ledger."""

    def __init__(
        self,
        account_number: str,
        amount: Decimal,
        accounting_type: AbstractEntryType,
        created_at: datetime = None,
        transaction_id: uuid.UUID = None,
        balance: Decimal = None,
    ):
        self.account_number = account_number
        self.amount = amount
        self.accounting_type = accounting_type
        self.balance = balance
        self.created_at = created_at
        self.transaction_id = transaction_id

    @classmethod
    def create_new(cls, account_number: str, amount: Decimal, accounting_type: AbstractEntryType):
        created_at = datetime.utcnow()
        transaction_id = uuid.uuid4()
        balance = None
        return cls(
            account_number=account_number,
            amount=amount,
            accounting_type=accounting_type,
            created_at=created_at,
            transaction_id=transaction_id,
            balance=balance,
        )

    def get_signed_amount(self) -> Decimal:
        """Returns the correctly signed amount."""
        return self.amount * self.accounting_type.get_sign()

    def get_accounting_type_code(self) -> str:
        """Returns a type code for this accounting type."""
        return self.accounting_type.get_type_code()


class Balance:
    """Maintains balance for an account."""

    @staticmethod
    def update_balance(entry: LedgerEntry):
        """Updates the account holder balance from a ledger entry."""
        balance_record = Balance._get_or_create_record(entry.account_number)
        balance_record.balance += entry.get_signed_amount()
        entry.balance = balance_record.balance
        balance_record.save()

    @staticmethod
    def _get_or_create_record(account_number: str) -> models.Balance:
        # Fetch account record from database or create a zero balance record if one doesn't exist.
        try:
            balance_entry = models.Balance.query.filter_by(account_number=account_number).one()
        except NoResultFound:
            balance_entry = models.Balance(account_number=account_number, balance=0)
        return balance_entry

    @staticmethod
    def get_for_account(account_number: str) -> Decimal:
        """Get the balance for an account."""
        balance_record = Balance._get_or_create_record(account_number)
        return balance_record.balance


class Ledger:
    """Public interface for updating the ledger and balance."""

    @classmethod
    def add_entry(cls, account_number: str, amount: Decimal, type_code: TypeCode) -> LedgerEntry:
        """Add entry to the ledger."""
        accounting_type = get_accounting_type(type_code)
        ledger_entry = LedgerEntry.create_new(account_number, amount, accounting_type)
        cls._store(ledger_entry)
        Balance.update_balance(ledger_entry)
        return ledger_entry

    @classmethod
    def _store(cls, ledger_entry: LedgerEntry):
        # Store ledger record in db.
        ledger_record = models.Ledger(
            account_number=ledger_entry.account_number,
            amount=ledger_entry.amount,
            accounting_type=ledger_entry.get_accounting_type_code(),
            transaction_id=str(ledger_entry.transaction_id),
            created_at=ledger_entry.created_at,
        )
        ledger_record.save()

    @classmethod
    def get_entries_for_account(cls, account_number: str) -> List[LedgerEntry]:
        """Return all ledger entries for an account."""
        query = models.Ledger.query.filter_by(account_number=account_number).order_by(
            models.Ledger.id.desc()
        )
        return cls._build_entries_from_query(account_number, query)

    @classmethod
    def get_entries_for_account_with_limit(cls, account_number: str, limit: int) -> List[LedgerEntry]:
        """Return up to the limited number of ledger entries for an account."""
        query = (
            models.Ledger.query.filter_by(account_number=account_number)
            .order_by(models.Ledger.id.desc())
            .limit(limit)
        )
        return cls._build_entries_from_query(account_number, query)

    @classmethod
    def _build_entries_from_query(cls, account_number: str, query: Query) -> List[LedgerEntry]:
        latest_balance = Balance.get_for_account(account_number)
        entries = []
        for record in query:
            entry = cls._record_to_entry(record)
            entry.balance = latest_balance
            entries.append(entry)
            latest_balance -= entry.get_signed_amount()
        return entries

    @classmethod
    def _record_to_entry(cls, record: models.Ledger) -> LedgerEntry:
        # Convert a db record to the entry type
        accounting_type = get_accounting_type(record.accounting_type)
        # DateTimes are stored in UTC, but retrieved as naive - we just need to add the timezone back.
        created_at_utc = record.created_at.replace(tzinfo=pytz.UTC)
        return LedgerEntry(
            account_number=record.account_number,
            amount=record.amount,
            accounting_type=accounting_type,
            transaction_id=record.transaction_id,
            created_at=created_at_utc,
        )
