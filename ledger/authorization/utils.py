from ledger.authorization.models import Token
from ledger.database import db


def token_is_valid(token: str) -> bool:
    """Checks token is present in db."""
    query = db.session.query(Token).filter(Token.access_token == token)
    return db.session.query(query.exists()).scalar()
