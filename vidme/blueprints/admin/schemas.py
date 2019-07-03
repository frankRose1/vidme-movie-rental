from marshmallow import fields, ValidationError, validate

from vidme.extensions import marshmallow
from vidme.blueprints.billing.schemas import (
    CreditCardSchema,
    SubscriptionSchema
)

USERNAME_MESSAGE = 'Username must be letters, numbers and underscores only.'


def validate_role(data):
    """Ensure the user role is either "member" or "admin"."""
    if data not in ['admin', 'member']:
        raise ValidationError('{0} is not a valid role.'.format(data))

    return data


class AdminEditUserschema(marshmallow.Schema):
    """
    Admins can change the user's username(if it goes against guidelines), and
    they can change a user's role from member to admin or vice versa
    """
    username = fields.Str(required=True,
                          validate=[validate.Length(min=3, max=255),
                                    validate.Regexp('^\w+$',
                                                    error=USERNAME_MESSAGE)])
    role = fields.Str(required=True, validate=validate_role)


class UserSchema(marshmallow.Schema):
    """For dumping a list of user data in the admin view."""
    # Nested schema for billing info/ subscription? TO show if a user has an
    #  account and to sort the results on the client
    class Meta:
        fields = ('username', 'email', 'role', 'sign_in_count',
                  'last_sign_in_on', 'created_on', 'payment_id')


class UserDetailSchema(marshmallow.Schema):
    """
    For dumping more detailed user info, inlcuding CC and billing information
    """
    class Meta:
        fields = ('email', 'username', 'name', 'role', 'sign_in_count',
                  'current_sign_in_on', 'current_sign_in_ip', 'updated_on',
                  'last_sign_in_on', 'last_sign_in_ip', 'created_on',
                  'credit_card', 'subscription', 'name',
                  'cancelled_subscription_on')
    # Use nested Schemas
    credit_card = fields.Nested(CreditCardSchema)
    subscription = fields.Nested(SubscriptionSchema)


admin_edit_user_schema = AdminEditUserschema()
users_schema = UserSchema(many=True)
user_detail_schema = UserDetailSchema()
