from decimal import Decimal

from ledger.ledger.accounting_types import TypeCode
from ledger.ledger.models import Ledger, Balance


def test_ledger_save_method(db_session):
    entry = Ledger(
        account_number="12323123", amount=Decimal("392.00"), accounting_type=TypeCode.CREDIT.value
    )
    entry.save()
    assert len(Ledger.query.filter_by(account_number="12323123").all()) == 1
    assert Ledger.query.filter_by(account_number="12323123").one() == entry


def test_balance_save_method(db_session):
    entry = Balance(account_number="234234423", balance=Decimal("23424.93"))
    entry.save()
    assert len(Balance.query.filter_by(account_number="234234423").all()) == 1
    assert Balance.query.filter_by(account_number="234234423").one() == entry


def test_ledger_representation(db_session):
    entry = Ledger(account_number="12323123", amount=Decimal("392.82"), accounting_type=TypeCode.DEBIT.value)
    assert str(entry) == "<Ledger: (id=None, account_number=12323123, amount=392.82, accounting_type=D)>"


def test_balance_representation(db_session):
    entry = Balance(account_number="234234423", balance=Decimal("23424.93"))
    assert str(entry) == "<Balance: (id=None, account_number=234234423, balance=23424.93)>"
