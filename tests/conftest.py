import os

import pytest

from ledger import create_app
from ledger.authorization.models import Token
from ledger.database import db as _db


TESTDB = "/tmp/test_project.db"
TEST_DATABASE_URI = f"sqlite:///{TESTDB}"


@pytest.fixture(scope="session")
def app(request):
    """Session-wide test `Flask` application."""
    settings_override = {"TESTING": True, "SQLALCHEMY_DATABASE_URI": TEST_DATABASE_URI}
    app = create_app(extra_config=settings_override)

    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)

    return app


@pytest.fixture(scope="session")
def client(app):
    client = app.test_client()
    yield client


@pytest.fixture(scope="session")
def authorized_client(client):
    client.environ_base["HTTP_AUTHORIZATION"] = "Token 8ldi2lD"
    yield client


@pytest.fixture(scope="session")
def db(app, request):
    """Session-wide test database."""
    if os.path.exists(TESTDB):
        os.unlink(TESTDB)

    def teardown():
        _db.drop_all()
        os.unlink(TESTDB)

    _db.app = app
    _db.create_all()

    request.addfinalizer(teardown)
    return _db


@pytest.fixture(scope="function")
def db_session(db, request):
    """Create a new database session for a test."""
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session = db.create_scoped_session(options=options)

    db.session = session

    token = Token(access_token="8ldi2lD")
    token.save()

    def teardown():
        transaction.rollback()
        connection.close()
        session.remove()

    request.addfinalizer(teardown)
    return session
