import pytest

from ledger.app.accounting_types import TypeCode, debit_type, get_accounting_type, credit_type


@pytest.mark.parametrize(
    "type_code,expected_type",
    [
        (TypeCode.DEBIT, debit_type),
        (TypeCode.CREDIT, credit_type),
        (TypeCode.DEBIT.value, debit_type),
        (TypeCode.CREDIT.value, credit_type),
    ],
)
def test_factory_method_retrieves_accounting_types(type_code, expected_type):
    retrieved_type = get_accounting_type(type_code)
    assert retrieved_type is expected_type
