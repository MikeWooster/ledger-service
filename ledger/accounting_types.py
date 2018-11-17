from enum import Enum


class TypeCode(Enum):
    CREDIT = 0
    DEBIT = 1


class AbstractEntryType:

    def get_sign(self) -> int:
        raise NotImplementedError  # pragma: no cover


class CreditType(AbstractEntryType):

    def get_sign(self) -> int:
        return 1

    def __str__(self):
        return "Credit"


class DebitType(AbstractEntryType):

    def get_sign(self) -> int:
        return -1

    def __str__(self):
        return "Debit"


credit_type = CreditType()
debit_type = DebitType()


entry_type_map = {
        TypeCode.CREDIT: credit_type,
        TypeCode.DEBIT: debit_type,
    }


def get_accounting_type(type_code: TypeCode) -> AbstractEntryType:
    return entry_type_map[type_code]
