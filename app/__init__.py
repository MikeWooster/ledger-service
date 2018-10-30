from flask import Flask

from app.ledger.controllers import blueprint as ledger_blueprint


# Define the WSGI application object
app = Flask(__name__)


# Configurations
app.config.from_object('config')


# Register blueprint(s)
app.register_blueprint(ledger_blueprint)
