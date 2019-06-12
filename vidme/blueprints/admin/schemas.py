from marshmallow import fields, ValidationError, validate

from vidme.extensions import marshmallow
from vidme.blueprints.user.models import User

USERNAME_MESSAGE = 'Username must be letters, numbers and underscores only.'

def validate_role(data):
    """Ensure the user role is either "member" or "admin"."""
    if data not in ['admin', 'member']:
        raise ValidationError('{0} is not a valid role.'.format(data))
    
    return data


class AdminEditUserschema(marshmallow.Schema):
    """
    Admins can change the user's username(if it goes against guidelines), and they can
    change a user's role from member to admin or vice versa
    """
    username = fields.Str(required=True, 
                        validate=[validate.Length(min=3, max=255),
                                validate.Regexp('^\w+$', message=USERNAME_MESSAGE)])
    role = fields.Str(required=True, validate=validate_role)


class UserSchema(marshmallow.Schema):
    """For dumping user data in the admin view."""
    class Meta:
        fields = ('id', 'email', 'username', 'role', 'sign_in_count',
                'current_sign_in_on', 'current_sign_in_ip', 'updated_on',
                'last_sign_in_on', 'last_sign_in_ip', 'created_on')


admin_edit_user_schema = AdminEditUserschema()
user_schema = UserSchema()
users_schema = UserSchema(many=True)
