import pytest

from config import settings
from vidme.app import create_app
from vidme.extensions import db as _db
from vidme.blueprints.user.models import User


@pytest.yield_fixture(scope='session')
def app():
    """
    Setup the flask test app, this only gets executed once at the start of the
    test suite.

    :return: Flask app
    """
    db_uri = '{0}_test'.format(settings.SQLALCHEMY_DATABASE_URI)
    params = {
        'DEBUG': False,
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': db_uri
    }

    _app = create_app(settings_override=params)

    # Establish application context before running
    ctx = _app.app_context()
    ctx.push()

    yield _app

    ctx.pop()


@pytest.yield_fixture(scope='function')
def client(app):
    """
    Setup an app client, this gets executed for each test function

    :param app: Pytest fixture
    :return: Flask app client
    """
    yield app.test_client()


@pytest.fixture(scope='session')
def db(app):
    """
    Set up test database, this only gets executed once per session.

    :param app: Pytest fixture
    :return: SQLAlchemy database session
    """

    _db.drop_all()
    _db.create_all()

    # Create a single user, a lot of tests will not mutate this user
    params = {
        'role': 'admin',
        'email': 'testAdmin@local.host',
        'username': 'testAdmin1',
        'password': 'password'
    }

    admin = User(**params)

    _db.session.add(admin)
    _db.session.commit()

    return _db


@pytest.yield_fixture(scope='function')
def session(db):
    """
    Allow very fast tests by using rollbacks and nested sessions. This does
    require that your database supports SQL savepoints, and Postgres does.

    :param db: Pytest fixture
    :return: None
    """
    db.session.begin_nested()

    yield db.session

    db.session.rollback()


@pytest.yield_fixture(scope='function')
def users(db):
    """
    Create user fixtures. They reset per test.

    :param db: Pytest fixture
    :return: SQLAlchemy database session
    """
    db.session.query(User).delete()

    users = [
        {
            'role': 'admin',
            'email': 'anotherAdmin@local.host',
            'username': 'secondAdmin2',
            'password': 'password'
        },
        {
            'email': 'member@local.host',
            'username': 'originalMember',
            'password': 'password'
        }
    ]

    for user in users:
        db.session.add(User(**user))

    db.session.commit()

    return db
