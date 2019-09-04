from datetime import timedelta
from distutils.utils import strtobool
import os


from celery.schedules import crontab

LOG_LEVEL = os.getenv('LOG_LEVEL', 'DEBUG')

SECRET_KEY = os.getenv('SECRET_KEY', None)

SERVER_NAME = os.getenv('SERVER_NAME',
                        'localhost:{0}'.format(os.getenv('DOCKER_WEB_PORT',
                                                          '8000')))

# SQLALchemy
pg_user = os.getenv('POSTGRES_USER', 'vidme')
pg_pass = os.getenv('POSTGRES_PASSWORD', 'password')
pg_host = os.getenv('POSTGRES_HOST', 'postgres')
pg_port = os.getenv('POSTGRES_PORT', '5432')
pg_db = os.getenv('POSTGRES_DB', pg_user)
db = 'postgresql://{0}:{1}@{2}:{3}/{4}'.format(pg_user, pg_pass,
                                               pg_host, pg_port, pg_db)                    os.environ['POSTGRES_DB'])
SQLALCHEMY_DATABASE_URI = db
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Flask-Mail
# if using gmail may need to "allow less secure apps"
# https://myaccount.google.com/lesssecureapps
MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
MAIL_PORT = os.getenv('MAIL_PORT', 587)
MAIL_USE_TLS = bool(strtobool(os.getenv('MAIL_USE_TLS', 'true')))
MAIL_USE_SSL = bool(strtobool(os.getenv('MAIL_USE_SSL', 'false')))
MAIL_USERNAME = os.getenv('MAIL_USERNAME', None)
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', None)
MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'smtp.gmail.com')

# Seed user
SEED_ADMIN_EMAIL = os.getenv('SEED_ADMIN_EMAIL', 'dev@local.host')
SEED_ADMIN_PASSWORD = os.getenv('SEED_ADMIN_PASSWORD', 'password')
SEED_ADMIN_USERNAME = os.getenv('SEED_ADMIN_USERNAME', 'devAdmin1')

# Celery
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://redis:6379/0')
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELEREY_REDIS_MAX_CONNECTIONS = 5
CELERYBEAT_SCHEDULE = {
    'mark-soon-to-expire-credit-cards': {
        'task': 'vidme.blueprints.billing.tasks.mark_old_credit_cards',
        'schedule': crontab(hour=0, minute=0)
    }
}

# Allow browsers to securely persist auth tokens(by default jwt_extened only checks headers) but also
# allow headers so that other clients can send an auth token too
JWT_TOKEN_LOCATION = ['cookies', 'headers']

# Only allows JWT cookies to be sent over HTTPS
# In production this should be True
JWT_COOKIE_SECURE = False

# When set to False cookies will persist even after the browser
# is closed
JWT_SESSION_COOKIE = False

# Expire tokens in 1 year(unrelated to the cookie's duration)
JWT_ACCESS_TOKEN_EXPIRES = timedelta(weeks=52)

# we are authenticating with this auth token for a number of endpoints
# if performance issues are a problem regarding sending cookies on every request
# then this may need to be changed
JWT_ACCESS_COOKIE_PATH = '/'

# Enable CSRF double submit protection (http://www.redotheweb.com/2015/11/09/api-security.html)
JWT_COOKIE_CSRF_PROTECT = True

# Stripe(publishable and secret key should go in instance.settings)
STRIPE_API_VERSION = '2018-02-28' # tell the stripe python project which version to use
STRIPE_PLANS = {
  '0': {
    'id': 'bronze',
    'name': 'Bronze',
    'amount': 499,
    'currency': 'usd',
    'interval': 'month',
    'interval_count': 1,
    'trial_period_days': 14,
    'statement_descriptor': 'VIDME BRONZE',
    'metadata': {}
  },
  '1': {
    'id': 'gold',
    'name': 'Gold',
    'amount': 999,
    'currency': 'usd',
    'interval': 'month',
    'interval_count': 1,
    'trial_period_days': 14,
    'statement_descriptor': 'VIDME GOLD',
    'metadata': {
      'recommended': True
    }
  },
  '2': {
    'id': 'platinum',
    'name': 'Platinum',
    'amount': 1299,
    'currency': 'usd',
    'interval': 'month',
    'interval_count': 1,
    'trial_period_days': 14,
    'statement_descriptor': 'VIDME PLATINUM',
    'metadata': {}
  },
}
