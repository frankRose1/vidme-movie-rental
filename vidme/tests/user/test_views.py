from flask import url_for

from lib.tests import assert_status_with_message, ViewTestMixin
# from vidme.blueprints.user.models import User


class TestRegister(ViewTestMixin):
    def test_register(self):
        """Register successfully"""
        user = {
            'email': 'newMember@local.host',
            'username': 'newMember2',
            'password': 'password'
        }
        response = self.client.post(url_for('UsersView:post'), json=user)
        print(response.data)
        assert response.status_code == 201
