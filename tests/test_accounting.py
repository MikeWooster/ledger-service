from decimal import Decimal

import pytest

from ledger.accounting import Ledger, Balance
from ledger.accounting_types import TypeCode


@pytest.mark.parametrize("type_code,type_str", [(TypeCode.CREDIT, "Credit"), (TypeCode.DEBIT, "Debit")])
def test_add_accounting_type_to_ledger(db_session, type_code, type_str):
    entry = Ledger.add_entry(account_number="39209030", amount=Decimal("1230.00"), type_code=type_code)
    assert len(Ledger.get_all_entries()) == 1
    assert entry.account_number == "39209030"
    assert entry.amount == Decimal("1230.00")
    assert str(entry.accounting_type) == type_str


def test_balance_is_updated(db_session):
    account_number = "39209030"
    Ledger.add_entry(account_number=account_number, amount=Decimal("1230.00"), type_code=TypeCode.CREDIT)
    assert Balance.get_for_account(account_number) == Decimal("1230.00")
    Ledger.add_entry(account_number=account_number, amount=Decimal("382.00"), type_code=TypeCode.DEBIT)
    assert Balance.get_for_account(account_number) == Decimal("848.00")
    Ledger.add_entry(account_number=account_number, amount=Decimal("921.00"), type_code=TypeCode.CREDIT)
    assert Balance.get_for_account(account_number) == Decimal("1769.00")
