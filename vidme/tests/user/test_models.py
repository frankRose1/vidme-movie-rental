from vidme.blueprints.user.models import User


class TestUser(object):
    def test_serialize_token(self, token):
        """User.serialize_token serializes a JWS correctly"""
        assert token.count('.') == 2

    def test_deserialize_token(self, token):
        """User.deserialize_token de-serializes a JWS correctly"""
        user = User.deserialize_token(token)
        assert user.email == 'testAdmin@local.host'

    def test_deserialize_token_tampered(self, token):
        """
        User.deserialize_token returns None if a token has been tampered with
        """
        tampered_token = 'hacked!!{0}'.format(token)
        user = User.deserialize_token(tampered_token)
        assert user is None
