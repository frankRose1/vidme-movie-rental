from vidme.app import create_celery_app
from vidme.blueprints.user.models import User

celery = create_celery_app()


@celery.task()
def delete_users(ids):
    """
    Delete users and potentially cancel their subscription.

    :param ids: List of ids to be deleted
    :type ids: list
    :return: int
    """
    return User.bulk_delete(ids)
