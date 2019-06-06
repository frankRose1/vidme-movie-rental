from datetime import timedelta
import os

DEBUG = True

db_uri = 'postgresql://{0}:{1}@postgres:5432/{2}'.format(os.environ['POSTGRES_USER'], 
                                                        os.environ['POSTGRES_PASSWORD'], 
                                                        os.environ['POSTGRES_DB'])

SQLALCHEMY_DATABASE_URI = db_uri
SQLALCHEMY_TRACK_MODIFICATIONS = False

SERVER_NAME = '192.168.99.100:8000' # if on Docker For Windows/Mac use "localhost:8000"
SECRET_KEY = 'notSoSecretDevelopmentKey'

# Allow browsers to securely persist auth tokens but also
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
JWT_ACCESS_COOKIE_PATH = '/'

# Enable CSRF double submit protection (http://www.redotheweb.com/2015/11/09/api-security.html)
JWT_COOKIE_CSRF_PROTECT = True