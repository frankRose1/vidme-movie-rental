import datetime

from lib.util_sqlalchemy import ResourceMixin
from vidme.extensions import db
from vidme.blueprints.billing.gateways.stripecom import Invoice as \
    PaymentInvoice


class Invoice(ResourceMixin, db.Model):
    __tablename__ = 'invoices'
    id = db.Column(db.Integer, primary_key=True)

    # Relationships
    user_id = db.Column(db.Integer, db.ForeignKey('users.id',
                                                  onupdate='CASCADE',
                                                  ondelete='CASCADE'),
                        index=True, nullable=False)

    # Invoice details (provided by stripe)
    plan = db.Column(db.String(128), index=True)
    receipt_number = db.Column(db.String(128), index=True)
    description = db.Column(db.String(128))
    period_start_on = db.Column(db.Date)
    period_end_on = db.Column(db.Date)
    currency = db.Column(db.String(8))
    tax = db.Column(db.Integer())
    tax_percent = db.Column(db.Float())
    total = db.Column(db.Integer())

    # De-normalize the card details so a users history can be shown properly
    # even if they have no active subscription or changed cards at some point
    # they would still want to see the CC related to a certain invoice
    brand = db.Column(db.String(32))
    last4 = db.Column(db.Integer)
    exp_date = db.Column(db.Date, index=True)

    def __init__(self, **kwargs):
        # Call Flask-SQLalchemy's constructor
        super(Invoice, self).__init__(**kwargs)

    @classmethod
    def _parse_from_api(cls, payload):
        """
        Parse the relevant invoice information

        :return: dict
        """
        plan_info = payload['lines']['data'][0]['plan']
        date = datetime.datetime.utcfromtimestamp(payload['date'])
        invoice = {
            'plan': plan_info['name'],
            'description': plan_info['statement_descriptor'],
            'next_bill_on': date,
            'amount_due': payload['amount_due'],
            'interval': plan_info['interval']
        }

        return invoice

    @classmethod
    def billing_history(cls, user=None):
        """
        Return the billing history for a specifc user.

        :param user: User who's billing history is being retrieved
        :type user: User instance
        :return: Invoices
        """
        invoices = Invoice.query.filter(Invoice.user_id == user.id) \
            .order_by(Invoice.created_on.desc()).limit(12)

        return invoices

    @classmethod
    def upcoming(cls, customer_id=None):
        """
        Return the upcoming invoice item for a specific user.

        :param customer_id: Customer's stripe ID
        :type customer_id: int
        :return: Stripe Invoice object
        """
        invoice = PaymentInvoice.upcoming(customer_id)

        return Invoice._parse_from_api(invoice)
