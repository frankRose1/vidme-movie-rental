from werkzeug.middleware.proxy_fix import ProxyFix
from flask import Flask, jsonify
from celery import Celery

import stripe

from vidme.blueprints.user.models import User
from vidme.api.auth import AuthView
from vidme.api.stripe_webhook import StripeWebhookView
from vidme.api.v1.user import UsersView
from vidme.api.v1.admin import AdminView
from vidme.api.v1.billing import (
    SubscriptionsView,
    PlansView,
    InvoicesView
)
from vidme.extensions import (
    jwt,
    db,
    marshmallow,
    mail
)

CELERY_TASK_LIST = [
    'vidme.blueprints.admin.tasks',
    'vidme.blueprints.user.tasks',
]


def create_celery_app(app=None):
    """
    Create a new Celery object and sync the Celery config to the Flask app's
    config. Wrap all tasks in the context of the Flask app.

    :param app: Flask app
    :return: Celery app
    """
    app = app or create_app()

    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'],
                    include=CELERY_TASK_LIST)

    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            # if the db is needed inside a task app context must be set
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery


def create_app(settings_override=None):
    """
    Create a Flask app using the app factory pattern.

    :param settings_override: Override app settings
    :return: Flask app
    """
    app = Flask(__name__)

    app.config.from_object('config.settings')

    if settings_override:
        app.config.update(settings_override)

    stripe.api_key = app.config.get('STRIPE_SECRET_KEY')
    stripe.api_version = app.config.get('STRIPE_API_VERSION')

    # register the API views
    AuthView.register(app)
    StripeWebhookView.register(app)
    UsersView.register(app)
    AdminView.register(app)
    SubscriptionsView.register(app)
    PlansView.register(app)
    InvoicesView.register(app)

    # add extensions
    extensions(app)

    # add custom jwt callbacks
    jwt_callbacks()

    return app


def extensions(app):
    """
    Add 0 or more extensions to the flask application.

    :param app: Flask application instance
    :return: None
    """
    jwt.init_app(app)
    db.init_app(app)
    marshmallow.init_app(app)
    mail.init_app(app)

    return None


def jwt_callbacks():
    """
    Set up custom behavior for JWT authentication.
    :return: None
    """
    @jwt.user_loader_callback_loader
    def user_loader_callback(identity):
        """
        This is called every time a user accesses a protected endpoint.
        "username" was the identity we used when creating the access_token
        """
        return User.query.filter(User.username == identity).first()

    @jwt.user_claims_loader
    def add_claims_to_access_token_callback(identity):
        """
        This is called every time an access token is created. It will add any
        additional info regarding the user to the access token. Identity
        (username) of the user is passed as a param. Will mainly be used to
        determine if a user is an admin or not.
        """
        user = User.query.filter(User.username == identity).first()
        return {
            'role': user.role
        }

    @jwt.unauthorized_loader
    def jwt_unauthorized_callback(error):
        response = {
            'error': {
                'message': 'Auth token was not provided.',
                'detail': error
            }
        }

        return jsonify(response), 401

    @jwt.expired_token_loader
    def jwt_expired_token_callback(error):
        response = {
            'error': {
                'message': 'Auth token has expired.'
            }
        }

        return jsonify(response), 401

    return None


def middleware(app):
    """
    Register 0 or more middleware (mutates the app passed in)

    :param app: Flask application instance
    :return: None
    """
    # Swap request.remote_addr with the real IP aaddress even if behind a proxy
    #This is necessary because we're tracking user's IP addresses
    app.wsgi_app = ProxyFix(app.wsgi_app)

    return None