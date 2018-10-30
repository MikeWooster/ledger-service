from enum import Enum


class TypeCode(Enum):
    CREDIT = 0
    DEBIT = 1


class AbstractEntryType:

    def get_sign(self) -> int:
        raise NotImplementedError


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


entry_type_map = {
        TypeCode.CREDIT: CreditType(),
        TypeCode.DEBIT: DebitType(),
    }


def create_entry_type(type_code: TypeCode) -> AbstractEntryType:
    return entry_type_map[type_code]
