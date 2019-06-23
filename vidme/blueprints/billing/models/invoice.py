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

    @classmethod
    def parse_from_event(cls, payload):
        """
        From a Stripe event, parse and return all of the data needed to save
        an Invoice locally.

        :return: dict
        """
        data = payload['data']['object']
        plan_info = data['lines']['data'][0]['plan']

        period_start_on = datetime.datetime.utcfromtimestamp(
            data['lines']['data'][0]['period']['start']).date()
        period_end_on = datetime.datetime.utcfromtimestamp(
            data['lines']['data'][0]['period']['end']).date()

        invoice = {
            'payment_id': data['customer'],
            'plan': plan_info['name'],
            'receipt_number': data['receipt_number'],
            'description': plan_info['statement_descriptor'],
            'period_start_on': period_start_on,
            'period_end_on': period_end_on,
            'currency': data['currency'],
            'tax': data['tax'],
            'tax_percent': data['tax_percent'],
            'total': data['total']
        }
        return invoice

    @classmethod
    def prepare_and_save(cls, parsed_event):
        """
        Potentially save an invoice after the necessary fields have been
        parsed from the stripe webhook event "invoice.created".
        :param parsed_event: Invoice data to be saved
        :type parsed_event: dict
        :return: User instance
        """
        # Avoid circular imports
        from vidme.blueprints.user.models import User

        # Only save the invoice if the user is valid
        id = parsed_event.get('payment_id')
        user = User.query.filter((User.payment_id == id)).first()

        if user and user.credit_card:
            parsed_event['user_id'] = user.id
            parsed_event['brand'] = user.credit_card.brand
            parsed_event['last4'] = user.credit_card.last4
            parsed_event['exp_date'] = user.credit_card.exp_date

            del parsed_event['payment_id']

            invoice = Invoice(**parsed_event)
            invoice.save()

        return user
