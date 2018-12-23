from flask import Blueprint

from ledger.ledger.controllers import Credit, Debit, LedgerView, AccountBalance


GET = "GET"
POST = "POST"


blueprint = Blueprint("ledger", __name__, url_prefix="/")


blueprint.add_url_rule(rule="/ledger/credit", methods=(POST,), view_func=Credit.as_view("credit"))
blueprint.add_url_rule(rule="/ledger/debit", methods=(POST,), view_func=Debit.as_view("debit"))
blueprint.add_url_rule(rule="/ledger", methods=(GET,), view_func=LedgerView.as_view("ledger"))
blueprint.add_url_rule(
    rule="/account/<account_number>/balance",
    methods=(GET,),
    view_func=AccountBalance.as_view("account_balance"),
)
