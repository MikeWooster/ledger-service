from ledger.database import db
from ledger.models import BaseModel


class Token(BaseModel):
    """Database model to store tokens."""

    id = db.Column(db.Integer, primary_key=True)
    access_token = db.Column(db.String(256))
