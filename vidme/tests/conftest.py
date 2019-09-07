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
from vidme.blueprints.billing.models.invoice import Invoice
from vidme.blueprints.billing.gateways.stripecom import (
    Event as PaymentEvent,
    Card as PaymentCard,
    Subscription as PaymentSubscription,
    Invoice as PaymentInvoice,
    Product as PaymentProduct
)


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
        'JWT_COOKIE_CSRF_PROTECT': False,
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
        'password': 'password',
        'active': True
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


@pytest.fixture(scope='session')
def token(db):
    """
    Serialize a JWS token.

    :param db: Pytest fixture
    :return: JWS token
    """
    user = User.find_by_identity('testAdmin@local.host')
    return user.serialize_token()


@pytest.yield_fixture(scope='function')
def users(db):
    """
    Create user fixtures. They reset per test.

    :param db: Pytest fixture
    :return: SQLAlchemy database session
    """
    # db.session.query(User).delete()

    users = [
        {
            'role': 'admin',
            'email': 'anotherAdmin@local.host',
            'username': 'secondAdmin2',
            'password': 'password'
        },
        {
            'email': 'member@local.host',
            'username': 'userMember',
            'password': 'password'
        }
    ]

    for user in users:
        exists = User.find_by_identity(user['username'])
        if exists:
            exists.delete()
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
            'last4': '4242',
            'exp_date': june_29_2019
        },
        {
            'user_id': 1,
            'brand': 'Visa',
            'last4': '4242',
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
    Create subscription fixutres.

    :param db: Pytest fixture
    :return: SQLAlchemy database session
    """
    subscriber = User.find_by_identity('subscriber@local.host')
    if subscriber:
        subscriber.delete()
    db.session.query(Subscription).delete()

    params = {
        'role': 'member',
        'email': 'subscriber@local.host',
        'username': 'firstSub1',
        'name': 'Subby',
        'payment_id': 'cus_000',
        'password': 'password',
        'active': True
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
        'last4': '4242',
        'exp_date': datetime.date(2019, 6, 1)
    }
    credit_card = CreditCard(**params)
    db.session.add(credit_card)

    db.session.commit()

    return db


@pytest.fixture(scope='function')
def invoices(db):
    """
    Create invoice fixtures.

    :param db: Pytest fixture
    :return: SQLAlchemy database session
    """
    db.session.query(Invoice).delete()

    trial_start = datetime.date(2019, 5, 1)
    trial_end = datetime.date(2019, 5, 15)

    june_29_2021 = datetime.datetime(2021, 6, 29, 0, 0, 0)
    june_29_2021 = pytz.utc.localize(june_29_2021)
    invoices = [
        {
            'plan': 'gold',
            'receipt_number': '0009000',
            'description': 'VIDME GOLD',
            'period_start_on': trial_start,
            'period_end_on': trial_end,
            'currency': 'usd',
            'tax': None,
            'tax_percent': None,
            'total': None,
            'user_id': 1,
            'brand': 'Visa',
            'last4': '4242',
            'exp_date': june_29_2021
        },
        {
            'plan': 'gold',
            'receipt_number': '0010000',
            'description': 'VIDME GOLD',
            'period_start_on': trial_end,
            'period_end_on': datetime.date(2019, 6, 15),
            'currency': 'usd',
            'tax': 1.4,
            'tax_percent': 0.02,
            'total': 999,
            'user_id': 1,
            'brand': 'Visa',
            'last4': '4242',
            'exp_date': june_29_2021
        },
    ]

    for invoice in invoices:
        db.session.add(Invoice(**invoice))

    db.session.commit()
    return db


@pytest.fixture(scope='session')
def mock_stripe():
    """
    Mock all of Stripe's API calls.
    """
    PaymentEvent.retrieve = Mock(return_value={})
    PaymentCard.update = Mock(return_value={})
    PaymentSubscription.update = Mock(return_value={})
    PaymentSubscription.cancel = Mock(return_value={})
    PaymentSubscription.create = Mock(return_value={})

    product_api = {
        "id": "prod_000",
        "type": "service",
        "name": "gold",
        "statement_descriptor": "GOLD MONTHLY"
    }
    PaymentProduct.retrieve = Mock(return_value=product_api)

    upcoming_invoice_api = {
        'date': 1433018770,
        'id': 'in_000',
        'period_start': 1433018770,
        'period_end': 1433018770,
        'lines': {
            'data': [
                {
                    'id': 'sub_000',
                    'object': 'line_item',
                    'type': 'subscription',
                    'livemode': True,
                    'amount': 0,
                    'currency': 'usd',
                    'proration': False,
                    'period': {
                        'start': 1433161742,
                        'end': 1434371342
                    },
                    'subscription': None,
                    'quantity': 1,
                    'plan': {
                        'interval': 'month',
                        'name': 'Gold',
                        'created': 1424879591,
                        'amount': 999,
                        'currency': 'usd',
                        'id': 'gold',
                        'object': 'plan',
                        'livemode': False,
                        'interval_count': 1,
                        'trial_period_days': 14,
                        'metadata': {
                        },
                        'nickname': 'Gold',
                        'product': 'prod_000',
                    },
                    'description': None,
                    'discountable': True,
                    'metadata': {
                    }
                }
            ],
            'total_count': 1,
            'object': 'list',
            'url': '/v1/invoices/in_000/lines'
        },
        'subtotal': 0,
        'total': 0,
        'customer': 'cus_000',
        'object': 'invoice',
        'attempted': True,
        'closed': True,
        'forgiven': False,
        'paid': True,
        'livemode': False,
        'attempt_count': 0,
        'amount_due': 500,
        'currency': 'usd',
        'starting_balance': 0,
        'ending_balance': 0,
        'next_payment_attempt': None,
        'webhooks_delivered_at': None,
        'charge': None,
        'discount': None,
        'application_fee': None,
        'subscription': 'sub_000',
        'tax_percent': None,
        'tax': None,
        'metadata': {
        },
        'statement_descriptor': None,
        'description': None,
        'receipt_number': None
    }
    PaymentInvoice.upcoming = Mock(return_value=upcoming_invoice_api)
