from marshmallow import fields, validate

from vidme.extensions import marshmallow


class CreateEditSubscriptionSchema(marshmallow.Schema):
    """The client will need to send a one-time use token provided by stripe.
    When a user sends their CC info to stripe, stripe will respond with a
    token that we can use on the server to set up a customer's subscription
    """
    stripe_token = fields.Str(
        required=True, validate=validate.Length(min=1, max=255))
    plan = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    customer_name = fields.Str(
        required=True, validate=validate.Length(min=1, max=255))


class CreditCardSchema(marshmallow.Schema):
    """
    CC info is different than the incoming data to set up a subscription.
    The credit card model will store info such as last 4 digits, CC brand, and
    expiration date.
    """
    class Meta:
        fields = ('id', 'created_on', 'updated_on', 'exp_date', 'is_expiring',
                  'last4', 'brand', 'user_id')


class SubscriptionSchema(marshmallow.Schema):
    class Meta:
        fields = ('id', 'created_on', 'updated_on', 'plan')


class InvoiceSchema(marshmallow.Schema):
    class Meta:
        fields = ('id', 'created_on', 'plan', 'receipt_number', 'description',
                  'period_start_on', 'period_end_on', 'currency', 'tax',
                  'tax_percent', 'total', 'brand', 'last4', 'exp_date')


create_edit_subscription_schema = CreateEditSubscriptionSchema()
credit_card_schema = CreditCardSchema()
subscription_schema = SubscriptionSchema()
invoices_schema = InvoiceSchema(many=True)
