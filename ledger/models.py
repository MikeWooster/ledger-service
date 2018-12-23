"""Abstract models."""
from ledger.database import db


class BaseModel(db.Model):
    """Abstract model from which all other models need to inherit from.

    Provides convenience methods:
        - save()

    """

    __abstract__ = True

    def save(self):
        db.session.add(self)
        db.session.commit()
