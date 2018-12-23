from flask import Blueprint

from ledger.ledger.controllers import CreditView, DebitView, LedgerView, AccountBalanceView


GET = "GET"
POST = "POST"


blueprint = Blueprint("ledger", __name__, url_prefix="/")


blueprint.add_url_rule(rule="/ledger/credit", methods=(POST,), view_func=CreditView.as_view("credit"))
blueprint.add_url_rule(rule="/ledger/debit", methods=(POST,), view_func=DebitView.as_view("debit"))
blueprint.add_url_rule(rule="/ledger", methods=(GET,), view_func=LedgerView.as_view("ledger"))
blueprint.add_url_rule(
    rule="/account/<account_number>/balance",
    methods=(GET,),
    view_func=AccountBalanceView.as_view("account_balance"),
)
