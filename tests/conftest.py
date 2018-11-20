import pytest
from flask_sqlalchemy import SQLAlchemy

from ledger import create_app
from ledger.accounting import Ledger, Balance
from ledger.database import db


@pytest.fixture(scope='session')
def app():
    """Flask app fixture."""
    app = create_app()
    return app


@pytest.fixture(scope='session')
def client(app):

    app.config['TESTING'] = True
    client = app.test_client()

    yield client


@pytest.fixture
def clean_session():
    """Clears all data before running test method."""
    if Ledger._ledger:
        Ledger._ledger = []
    yield


@pytest.fixture(scope='session')
def _db(app):
    '''
    Provide the transactional fixtures with access to the database via a Flask-SQLAlchemy
    database connection.
    '''
    return db
