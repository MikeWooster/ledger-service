from flask import Blueprint

from ledger.app.controllers import CreditView, DebitView, TransactionHistoryView, AccountBalanceView


GET = "GET"
POST = "POST"


blueprint = Blueprint("ledger", __name__, url_prefix="/")


blueprint.add_url_rule(rule="/ledger/credit", methods=(POST,), view_func=CreditView.as_view("credit"))
blueprint.add_url_rule(rule="/ledger/debit", methods=(POST,), view_func=DebitView.as_view("debit"))
blueprint.add_url_rule(
    rule="/account/<account_number>/transactions",
    methods=(GET,),
    view_func=TransactionHistoryView.as_view("transactions"),
)
blueprint.add_url_rule(
    rule="/account/<account_number>/balance",
    methods=(GET,),
    view_func=AccountBalanceView.as_view("account_balance"),
)
