from flask import Flask, jsonify

from vidme.blueprints.user.models import User
from vidme.api.auth import AuthView
from vidme.api.v1.user import UsersView
from vidme.api.v1.admin import AdminView

from vidme.extensions import (
    jwt,
    db,
    marshmallow
)


def create_app(settings_override=None):
    """
    Create a Flask app using the app factory pattern.

    :param setting_override: Override app settings
    :return: Flask app
    """
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_object('config.settings')
    app.config.from_pyfile('settings.py', silent=True)

    if settings_override:
        app.config.update(settings_override)

    # register the API views
    AuthView.register(app)
    UsersView.register(app)
    AdminView.register(app)

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

    @jwt.unauthorized_loader
    def jwt_unauthorized_callback():
        response = {
            'error': {
                'message': 'Auth token was not provided.'
            }
        }

        return jsonify(response), 401

    @jwt.expired_token_loader
    def jwt_expired_token_callback():
        response = {
            'error': {
                'message': 'Auth token has expired.'
            }
        }

        return jsonify(response), 401

    return None
