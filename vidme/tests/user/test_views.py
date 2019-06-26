from flask import url_for

from lib.tests import assert_status_with_message, ViewTestMixin


class TestRegister(ViewTestMixin):
    def test_invalid_input(self):
        """Missing required fields"""
        data = {}
        response = self.client.post(url_for('UsersView:post'), json=data)
        assert_status_with_message(400, response, 'Invalid input.')

    def test_invalid_password(self):
        """Password fails schema validation"""
        data = {
            'password': '2short',
            'email': 'testMember@local.host',
            'username': 'testMember2',
        }
        response = self.client.post(url_for('UsersView:post'), json=data)
        assert response.status_code == 422

    def test_invalid_username(self):
        """Username fails schema validation"""
        data = {
            'username': 'no spaces allowed',
            'password': 'password',
            'email': 'testMember@local.host',
        }
        response = self.client.post(url_for('UsersView:post'), json=data)
        assert response.status_code == 422

    def test_invalid_email(self):
        """Email fails schema validation"""
        data = {
            'email': 'notAnEmail',
            'username': 'testMember2',
            'password': 'password',
        }
        response = self.client.post(url_for('UsersView:post'), json=data)
        assert response.status_code == 422

    def test_unique_username(self):
        """Username must be unique"""
        data = {
            'username': 'testAdmin1',
            'password': 'password',
            'email': 'testMember@local.host',
        }
        response = self.client.post(url_for('UsersView:post'), json=data)
        assert response.status_code == 422

    def test_unique_email(self):
        """Email must be unique"""
        data = {
            'email': 'testAdmin@local.host',
            'username': 'testMember2',
            'password': 'password',
        }
        response = self.client.post(url_for('UsersView:post'), json=data)
        assert response.status_code == 422

    def test_register(self):
        """Register successfully"""
        user = {
            'email': 'testMember@local.host',
            'username': 'testMember2',
            'password': 'password'
        }
        response = self.client.post(url_for('UsersView:post'), json=user)
        assert response.status_code == 201
