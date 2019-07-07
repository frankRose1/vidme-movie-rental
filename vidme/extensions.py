"""
    Init an instance of each extension used in the flask application here
"""
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_mail import Mail

jwt = JWTManager()
db = SQLAlchemy()
marshmallow = Marshmallow()
mail = Mail()
