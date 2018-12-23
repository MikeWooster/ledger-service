from flask import Flask
from flask_migrate import Migrate


def create_app(extra_config=None):
    app = Flask(__name__)

    from ledger import settings

    app.config.from_object(settings)
    app.config.update(extra_config or {})

    from ledger.database import db

    db.init_app(app)
    Migrate(app, db)

    from ledger.urls import blueprint as ledger_blueprint

    app.register_blueprint(ledger_blueprint)

    return app
