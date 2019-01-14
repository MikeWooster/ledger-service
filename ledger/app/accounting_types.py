from enum import Enum


class TypeCode(Enum):
    """TypeCode Enumerator."""

    CREDIT = "C"
    DEBIT = "D"


class AbstractEntryType:
    """Abstract implementation of the accounting types."""

    _sign = None
    _type_code_value = None
    _str = None

    def get_sign(self) -> int:
        return self._sign

    def get_type_code(self) -> str:
        return self._type_code_value

    def __str__(self) -> str:
        return self._str


class CreditType(AbstractEntryType):
    """Implementation of the credit type."""

    _sign = 1
    _type_code_value = TypeCode.CREDIT.value
    _str = "Credit"


class DebitType(AbstractEntryType):
    """Implementation of the debit type."""

    _sign = -1
    _type_code_value = TypeCode.DEBIT.value
    _str = "Debit"


credit_type = CreditType()
debit_type = DebitType()


entry_type_map = {
    TypeCode.CREDIT: credit_type,
    TypeCode.DEBIT: debit_type,
    TypeCode.CREDIT.value: credit_type,
    TypeCode.DEBIT.value: debit_type,
}


def get_accounting_type(type_code: TypeCode) -> AbstractEntryType:
    """Factory to get the correct accounting type given the defined string representation."""
    return entry_type_map[type_code]
