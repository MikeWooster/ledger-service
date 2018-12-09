from enum import Enum


class TypeCode(Enum):
    CREDIT = "C"
    DEBIT = "D"


class AbstractEntryType:
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
    _sign = 1
    _type_code_value = TypeCode.CREDIT.value
    _str = "Credit"


class DebitType(AbstractEntryType):
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
    return entry_type_map[type_code]
