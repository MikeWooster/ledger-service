from flask import Flask


def create_app():
    app = Flask(__name__)

    from ledger.controllers import blueprint as ledger_blueprint
    app.register_blueprint(ledger_blueprint)

    return app
