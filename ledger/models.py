from ledger.database import db


class BaseModel(db.Model):
    __abstract__ = True

    def save(self):
        db.session.add(self)
        db.session.commit()


class Ledger(BaseModel):
    __tablename__ = "ledger"
    id = db.Column(db.Integer, primary_key=True)
    account_number = db.Column(db.String(16))
    amount = db.Column(db.Integer)
    accounting_type = db.Column(db.String(1))

    def __repr__(self):
        return (
            f"<Ledger: (id={self.id}, account_number="
            f"{self.account_number}, amount={self.amount}, "
            f"accounting_type={self.accounting_type})>"
        )


class Balance(BaseModel):
    __tablename__ = "balance"
    id = db.Column(db.Integer, primary_key=True)
    account_number = db.Column(db.String(16), index=True, unique=True)
    balance = db.Column(db.Integer)

    def __repr__(self):
        return (
            f"<Balance: (id={self.id}, account_number="
            f"{self.account_number}, balance={self.balance})>"
        )
