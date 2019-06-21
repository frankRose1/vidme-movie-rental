import datetime

import pytz

from config import settings
from lib.util_sqlalchemy import ResourceMixin
from vidme.extensions import db
from vidme.blueprints.billing.models.credit_card import CreditCard
from vidme.blueprints.billing.gateways.stripecom import Card as PaymentCard
from vidme.blueprints.billing.gateways.stripecom import \
    Subscription as PaymentSubscription


class Subscription(ResourceMixin, db.Model):
    __tablename__ = 'subscriptions'
    id = db.Column(db.Integer, primary_key=True)

    # Relationships
    user_id = db.Column(db.Integer, db.ForeignKey('users.id',
                                                  onupdate='CASCADE',
                                                  ondelete='CASCADE'),
                        index=True, nullable=False)

    # Subscription details
    plan = db.Column(db.String(128))

    def __init__(self, **kwargs):
        # Call flask sql alchemy constructor
        super(Subscription, self).__init__(**kwargs)

    @classmethod
    def get_all_plans(cls):
        """
        Return a dict of all stripe plans in config.settings

        :return: Dict
        """
        stripe_plans = settings.STRIPE_PLANS
        plans = {}
        for key in stripe_plans:
            plans[stripe_plans[key].get('id')] = stripe_plans[key]

        return plans

    @classmethod
    def get_plan(cls, plan):
        """
        Get the plan based on the plan identifier

        :param plan: Plan identifier
        :type plan: str
        :return: Dict or None
        """
        for key, value in settings.STRIPE_PLANS.items():
            if value.get('id') == plan:
                return settings.STRIPE_PLANS[key]

        return None

    def cancel(self, user=None, discard_credit_card=True):
        """Delete a user's subscription and stop any future billing.

        :param user: User whos subscription is being deleted
        :type user: User instance
        :param discard_credit_card: Delete a user's related CreditCard
        :type discard_credit_card: bool

        :return: bool
        """
        PaymentSubscription.cancel(customer_id=user.payment_id)
        # update the user model's billing info
        user.payment_id = None
        user.cancelled_subscription_on = datetime.datetime.now(pytz.utc)
        db.session.add(user)
        # delete the related subscription model
        db.session.delete(user.subscription)

        if discard_credit_card:
            db.session.delete(user.subscription)

        db.session.commit()

        return True

    def update(self, user=None, plan=None):
        """
        Update the users subscription plan out of the available options:
        bronze, gold, or platiunum

        :param user: User whos subscription is being updated
        :type user: User instance
        :param: Plan being updated
        :type plan: str

        :return: bool
        """
        # update the users sub plan on Stripe
        PaymentSubscription.update(customer_id=user.payment_id, plan=plan)
        # update the user's sub plan in our DB
        user.subscription.plan = plan
        db.session.add(user.subscription)
        db.session.commit()

        return True

    def create(self, user=None, name=None, plan=None, token=None):
        """
        Create a recurring subscription

        :param user: User to apply the subscription to
        :type user: User instance
        :param name: User's billing name
        :type name: str
        :param plan: Plan to subscribe to
        :type plan: str
        :param token: One-time use token provided by stripe
        :type token: str

        :return: boolean
        """
        if token is None:
            return False

        # use the stripe gateway to create a new subscription
        customer = PaymentSubscription.create(token=token,
                                              email=user.email,
                                              plan=plan)

        # update the user account
        user.payment_id = customer.id
        user.name = name
        user.cancelled_subscription_on = None

        self.user_id = user.id
        self.plan = plan

        # create the credit card model
        credit_card = CreditCard(user_id=user.id,
                                 **CreditCard.extract_card_params(customer))

        # add and commit all newly created models
        db.session.add(user)
        db.session.add(credit_card)
        db.session.add(self)
        db.session.commit()

        return True

    def update_payment_method(self, user=None, credit_card=None,
                              name=None, token=None):
        """
        Update the subscription

        :param user: User to modify
        :type user: User instance
        :param credit_card: Card to modify
        :type credit_card: CreditCard instance
        :param name: User's billing name
        :type name: str
        :param token: Token provided by stripe
        :type token: str
        :return: bool
        """
        if token is None:
            return False

        # update the payment info on stripes API
        customer = PaymentCard.update(user.payment_id, token)

        user.name = name

        # Update the CC
        new_card = CreditCard.extract_card_params(customer)
        credit_card.brand = new_card.get('brand')
        credit_card.last4 = new_card.get('last4')
        credit_card.exp_date = new_card.get('exp_date')
        credit_card.is_expiring = new_card.get('is_expiring')

        db.session.add(user)
        db.session.add(credit_card)
        db.session.commit()

        return True
