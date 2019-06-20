from marshmallow import fields, validate

from vidme.extensions import marshmallow


class CreditCardSchema(marshmallow.Schema):
    """The client will need to send a one-time use token provided by stripe.
    When a user sends their CC info to stripe, stripe will respond with a
    token that we can use on the server to set up a customer's subscription
    """
    stripe_token = fields.Str(
        required=True, validate=validate.Length(min=1, max=255))
    plan = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    customer_name = fields.Str(
        required=True, validate=validate.Length(min=1, max=255))


credit_card_schema = CreditCardSchema()
