from flask import Flask

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
    
    # register blueprints
    
    # add extensions
    extensions(app)

    return app


def extensions(app):
    """
    Add 0 or more extensions to the flask application.

    :param app: Flask application instance
    :return: None
    """
    # eg jwt_extended.init_app(app)
    return None