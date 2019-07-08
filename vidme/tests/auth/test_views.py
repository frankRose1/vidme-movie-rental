from flask import url_for

from lib.tests import ViewTestMixin, assert_status_with_message


class TestAuthenticate(ViewTestMixin):
    def test_invalid_input(self):
        """Missing required fields"""
        response = self.client.post(url_for('AuthView:post'))
        assert_status_with_message(400, response, 'Invalid input.')

    def test_invalid_password(self):
        """Password fails schema validation"""
        data = {
            'password': 'pas',
            'identity': 'testAdmin1'
        }
        response = self.client.post(url_for('AuthView:post'), json=data)
        assert response.status_code == 422

    def test_invalid_identity(self):
        """Identity fails schema validation"""
        data = {
            'identity': 'te',
            'password': 'password'
        }
        response = self.client.post(url_for('AuthView:post'), json=data)
        assert response.status_code == 422

    def test_identity_no_exist(self):
        """Identity does not exist"""
        data = {
            'identity': 'doesNotExist',
            'password': 'password'
        }
        response = self.client.post(url_for('AuthView:post'), json=data)
        assert_status_with_message(401, response, 'Invalid credentials.')

    def test_incorrect_password(self):
        """Password does not match the stored hash"""
        data = {
            'identity': 'testAdmin1',
            'password': 'incorrectPassword'
        }
        response = self.client.post(url_for('AuthView:post'), json=data)
        assert_status_with_message(401, response, 'Invalid credentials.')

    def test_account_not_active(self, users):
        """Return a 400 if a user's account has not been activated"""
        data = {
            'identity': 'member@local.host',
            'password': 'password'
        }
        response = self.client.post(url_for('AuthView:post'), json=data)
        message = ('This account is not active. If you recently signed up for'
                   ' an account, check your email for a verification link.')
        assert_status_with_message(400, response, message)

    def test_authenticate(self):
        """Return an access token for valid crdentials"""
        data = {
            'identity': 'testAdmin1',
            'password': 'password'
        }
        response = self.client.post(url_for('AuthView:post'), json=data)
        json_data = response.get_json()['data']

        assert response.status_code == 200
        assert 'access_token' in json_data
