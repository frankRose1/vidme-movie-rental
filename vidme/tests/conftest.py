import datetime

import pytest
import pytz
from mock import Mock

from config import settings
from vidme.app import create_app
from vidme.extensions import db as _db
from lib.util_datetime import timedelta_months
from vidme.blueprints.user.models import User
from vidme.blueprints.billing.models.credit_card import CreditCard
from vidme.blueprints.billing.models.subscription import Subscription
from vidme.blueprints.billing.gateways.stripecom import \
    Event as PaymentEvent
from vidme.blueprints.billing.gateways.stripecom import Card as PaymentCard
from vidme.blueprints.billing.gateways.stripecom import \
    Subscription as PaymentSubscription
from vidme.blueprints.billing.gateways.stripecom import \
    Invoice as PaymentInvoice


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


@pytest.fixture(scope='function')
def credit_cards(db):
    """
    Create credit card fixtures.

    :param db: Pytest fixture
    :return: SQLAlchemy database session
    """
    db.session.query(CreditCard).delete()

    may_29_2019 = datetime.date(2019, 5, 29)
    june_29_2019 = datetime.datetime(2019, 6, 29, 0, 0, 0)
    june_29_2019 = pytz.utc.localize(june_29_2019)

    credit_cards = [
        {
            'user_id': 1,
            'brand': 'Visa',
            'last4': 4242
            'exp_date': june_29_2019
        },
        {
            'user_id': 1,
            'brand': 'Visa',
            'last4': 4242
            'exp_date': timedelta_months(12, may_29_2019)
        },
    ]

    for card in credit_cards:
        db.session.add(CreditCard(**card))

    db.session.commit()
    return db


@pytest.fixture(scope='function')
def subscriptions(db):
    """
    Create credit card fixtures.

    :param db: Pytest fixture
    :return: SQLAlchemy database session   
    """
    subscriber = User.find_by_identity('subscriber@local.host')
    if subscriber:
        subscriber.delete()
    db.session.Query.delete(Subscription).delete()

    params = {
        'role': 'admin',
        'email': 'subscriber@local.host',
        'username': 'firstSub1'
        'name': 'Subby',
        'payment_id': 'cus_00',
        'password': 'password'
    }

    subscriber = User(**params)
    # User needs to be commited to be able to assign a subscription to it
    db.session.add(subscriber)
    db.session.commit()

    # Create a subscription
    params = {
        'user_id': subscriber.id,
        'plan': 'gold'
    }
    subscription = Subscription(**params)
    db.session.add(subscription)

    # Create the users CC
    params = {
        'user_id': subscriber.id,
        'brand': 'Visa',
        'last4': 4242,
        'exp_date': datetime.date(2019, 6, 1)
    }
    credit_card = CreditCard(**params)
    db.session.add(credit_card)

    db.session.commit()

    return db


@pytest.fixture(scope='session')
def mock_stripe():
    """
    Mock all of Stripe's API calls.
    """
    PaymentEvent.retrieve = Mock(return_value={})
    PaymentCard.update = Mock(return_value={})
    PaymentSubscription.create = Mock(return_value={})
    PaymentSubscription.update = Mock(return_value={})
    PaymentSubscription.cancel = Mock(return_value={})

    upcoming_invoice_api = {}
