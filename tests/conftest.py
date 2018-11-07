import pytest

from ledger import create_app
from ledger.accounting import Ledger, Balance


@pytest.fixture
def app():
    """Flask app fixture."""
    app = create_app()
    return app


@pytest.fixture
def client(app):

    app.config['TESTING'] = True
    client = app.test_client()

    yield client


@pytest.fixture
def clean_session():
    """Clears all data before running test method."""
    if Ledger._ledger:
        Ledger._ledger = []
    if Balance._balances:
        Balance._balances = {}
    yield
