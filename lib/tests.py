import pytest
from flask import url_for


def assert_status_with_message(status_code=200, response=None, message=None):
    """
    Check to see if a message is contained within a response

    :param status_code: Status code that defaults to 200
    :type status_code: int

    :param response: Flask response
    :type response: str

    :param message: String to check for
    :type message: str

    :return: None
    """
    assert response.status_code == status_code
    assert message in str(response.data)


class ViewTestMixin(object):
    """
    Automatically load in a session and client. To be used on view tests.
    """

    @pytest.fixture(autouse=True)
    def set_common_fixtures(self, session, client):
        self.session = session
        self.client = client

    def authenticate(self, identity='testAdmin@local.host', password='password'):
        """Authenticate a specific user"""
        return _login(self.client, identity, password)


def _login(client, identity, password):
    """
    Log a specific user in by adding an auth token to the test client headers.

    :param client: Flask client
    :param identity: The user's identity(username or email)
    :type identity: str
    :param password: The password
    :type password: str
    :return: Flask test client
    """
    user = dict(identity=identity, password=password)

    response = client.post(url_for('AuthView:post'), json=user)
    data = response.get_json()['data']
    token = data['access_token']

    client.environ_base['HTTP_AUTHORIZATION'] = 'Bearer ' + token
    return client
