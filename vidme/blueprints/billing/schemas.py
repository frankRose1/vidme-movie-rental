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


class BillingInfoSchema(marshmallow.Schema):
    """
    Billing info is different than the incoming data to set up a subscription.
    The credit card model will store info such as last 4 digits, CC brand, and
    expiration date.
    """
    class Meta:
        fields = ('id', 'created_on', 'updated_on', 'exp_date', 'is_expiring',
                  'last4', 'brand')


create_edit_subscription_schema = CreateEditSubscriptionSchema()
billing_info_schema = BillingInfoSchema()
