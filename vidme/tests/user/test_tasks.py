from vidme.extensions import mail
from vidme.blueprints.user.tasks import deliver_verification_email
from vidme.blueprints.user.models import User


class TestTasks(object):
    def test_deliver_verification_email(self, token):
        """Successfully deliver a verification email"""
        with mail.record_messages() as outbox:
            user = User.find_by_identity('testAdmin@local.host')
            deliver_verification_email(user.id, token)

            assert len(outbox) == 1
            assert token in outbox[0].body
