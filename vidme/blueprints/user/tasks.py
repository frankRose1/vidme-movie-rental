from lib.flask_mailplus import send_template_message
from vidme.app import create_celery_app
from vidme.blueprints.user.models import User

celery = create_celery_app()


@celery.task()
def deliver_verification_email(user_id, activation_token):
    """
    Send an email to a user to verify their account.

    :param user_id: The user's ID
    :type user_id: int
    :param activation_token: The activation token
    :type activation_token: str
    :return: None if a user was not found
    """
    user = User.query.get(user_id)

    if user is None:
        return None

    ctx = {'user': user, 'activation_token':activation_token}

    send_template_message(subject='Account Verification From VidMe',
                          recipients=[user.email],
                          template='mail/user/verify_email', ctx=ctx)

    return None
