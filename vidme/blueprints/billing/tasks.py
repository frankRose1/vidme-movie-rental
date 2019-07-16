from vidme.app import create_celery_app
from vidme.blueprints.billing.models.credit_card import CreditCard

celery = create_celery_app()


@celery.task()
def mark_old_credit_cards():
    """
    Mark credit cards that are going to expire soon or that have already
    expired. This task will be run every day at midnight. See config.settings
    CELERYBEAT_SCHEDULE

    :return: Result of updating the records
    """
    return CreditCard.mark_old_credit_cards()
