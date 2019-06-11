import datetime
import pytz

from collections import OrderedDict
from werkzeug.security import generate_password_hash, check_password_hash

from lib.util_sqlalchemy import ResourceMixin, AwareDateTime
from vidme.extensions import db


class User(ResourceMixin, db.Model):
    ROLE = OrderedDict([
        ('member', 'Member'),
        ('admin', 'Admin')
    ])

    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)

    # Auth
    role = db.Column(db.Enum(*ROLE, name='role_types', native_enum=False),
                     index=True, nullable=False, server_default='member')
    username = db.Column(db.String(24), unique=True, index=True)
    email = db.Column(db.String(255), unique=True, index=True, nullable=False,
                      server_default='')
    password = db.Column(db.String(128), nullable=False, server_default='')

    # Activity tracking
    sign_in_count = db.Column(db.Integer, nullable=False, default=0)
    current_sign_in_on = db.Column(AwareDateTime())
    current_sign_in_ip = db.Column(db.String(45))
    last_sign_in_on = db.Column(AwareDateTime())
    last_sign_in_ip = db.Column(db.String(45))

    def __init__(self, **kwargs):
        # Call Flask_SQLAlchemy's constructor
        super(User, self).__init__(**kwargs)

        self.password = User.encrypt_password(kwargs.get('password', ''))

    @classmethod
    def find_by_identity(cls, identity):
        """
        Find a user by their e-mail or username.

        :param identity: Email or username
        :type identity" str

        :return: User instance
        """
        return User.query.filter(
            (User.email == identity) | (User.username == identity)).first()

    @classmethod
    def encrypt_password(cls, plaintext_password):
        """
        Hash a plaintext string using PBKDF2.

        :param plaintext_password: Password in plain text
        :type plaintext_password: str

        :return: str
        """
        if plaintext_password:
            return generate_password_hash(plaintext_password)

        return None

    def authenticated(self, with_password=True, password=''):
        """
        Ensure a user is authenticated, and optionally check their password

        :param with_password: Optionally check user's password
        :type with_password: bool

        :param password: Optionally verify this as their password
        :type password: str

        :return: bool
        """
        if with_password:
            return check_password_hash(self.password, password)

        return True

    def update_activity_tracking(self, ip_address):
        """
        Update various fields on the user that's related to meta data on their
        account, such as sign_in_count and ip_address, etc...

        :param ip_address: IP address
        :type ip_address: str

        :return: SQLAlchemy commit results
        """
        self.sign_in_count += 1

        self.last_sign_in_on = self.current_sign_in_on
        self.last_sign_in_ip = self.current_sign_in_ip

        self.current_sign_in_on = datetime.datetime.now(pytz.utc)
        self.current_sign_in_ip = ip_address

        return self.save()
