from flask import Flask


def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    from ledger.database import db
    db.init_app(app)

    from ledger.controllers import blueprint as ledger_blueprint
    app.register_blueprint(ledger_blueprint)

    return app
