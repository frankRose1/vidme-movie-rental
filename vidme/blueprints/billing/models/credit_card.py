import datetime

from lib.util_datetime import timedelta_months
from lib.util_sqlalchemy import ResourceMixin
from vidme.extensions import db


class CreditCard(ResourceMixin, db.Model):
    IS_EXPIRING_THRESHOLD_MONTHS = 2

    id = db.Column(db.Integer, primary_key=True)

    # Relationships
    user_id = db.Column(db.Integer, db.ForeignKey('users.id',
                                                   onupdate='CASCADE',
                                                   ondelete='CASCADE'),
                        index=True, nullable=False)

    # Card details
    brand = db.Column(db.String(32))
    last4 = db.Column(db.Integer)
    exp_date = db.Column(db.Date, index=True)
    is_expiring = db.Column(db.Boolean(), nullable=False, server_default='0')

    def __init__(self, **kwargs):
        # Call Flask-SQLAlchemy's constructor
        super(CreditCard, self).__init__(**kwargs)

    @classmethod
    def is_expiring_soon(cls, exp_date):
        """
        Determine if a a credit card is expiring soon.

        :return: boolean
        """
        pass

    @classmethod
    def extract_card_params(customer):
        """
        Extract the CC info from a payment customer object.

        :param customer: Payment customer from stripe
        :type customer: Payment customer
        :return: dict
        """
        card_data = customer.sources.data[0]
        exp_date = datetime.date(card_data.exp_year, card_data.exp_month, 1)

        card = {
            'brand': card_data.brand,
            'last4': card_data.last4,
            'exp_date': exp_date,
            'is_expiring': CreditCard.is_expiring_soon(exp_date=exp_date)
        }
        return card
