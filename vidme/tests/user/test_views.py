from flask import url_for

from lib.tests import assert_status_with_message, ViewTestMixin
from vidme.blueprints.user.models import User

# to run the test suite from inside the docker container
# docker-compose exec web py.test vidme/tests
# exec lets us run a command inside of a docker container. "web" is what we named the service in the docker-compose.yml

# each test gets the client fixture passed in
class TestRegister(ViewTestMixin):
    def test_register(self):
        """Register successfully"""
        data = {
            'email': 'newMember@local.host',
            'username': 'newMember2',
            'password': 'password'
        }
        response = self.client.post(url_for('UserView:post'), data=data)
        print(response.data)
        assert response.status_code == 200

