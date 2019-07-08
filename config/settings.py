from datetime import timedelta
import os

DEBUG = True

SERVER_NAME = '192.168.99.100:8000' # if on Docker For Windows/Mac use "localhost:8000"
SECRET_KEY = 'notSoSecretDevelopmentKey'

# SQLALchemy
db_uri = 'postgresql://{0}:{1}@postgres:5432/{2}'.format(os.environ['POSTGRES_USER'], 
                                                        os.environ['POSTGRES_PASSWORD'], 
                                                        os.environ['POSTGRES_DB'])
SQLALCHEMY_DATABASE_URI = db_uri
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Flask-Mail
# if using gmail may need to "allow less secure apps"
# https://myaccount.google.com/lesssecureapps
MAIL_DEFAULT_SENDER = 'contact@local.host'
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USE_SSL = False
MAIL_USERNAME = 'you@gmail.com'
MAIL_PASSWORD = 'yourpassword'

# Seed user
SEED_ADMIN_EMAIL = 'dev@local.host'
SEED_ADMIN_PASSWORD = 'devPassword'
SEED_ADMIN_USERNAME = 'devAdmin1'

# Celery
CELERY_BROKER_URL = 'redis://:devpassword@redis:6379/0'
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELEREY_REDIS_MAX_CONNECTIONS = 5

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
