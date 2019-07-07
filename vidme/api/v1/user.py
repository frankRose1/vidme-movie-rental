from flask import request, url_for
from flask_classful import route

from vidme.api import JSONViewMixin
from vidme.api.v1 import V1FlaskView
from vidme.blueprints.user.models import User
from vidme.blueprints.user.schemas import registration_schema


class UsersView(JSONViewMixin, V1FlaskView):
    def post(self):
        json_data = request.get_json()

        if not json_data:
            response ={'error': 'Invalid input.'}
            return response, 400

        data, errors = registration_schema.load(json_data)

        if errors:
            response = {'error': errors}
            return response, 422

        user = User()
        user.email = data.get('email')
        user.username = data.get('username')
        user.password = User.encrypt_password(data.get('password'))
        user.save()

        # send verification email with celery as a background task
        User.init_verify_email(user.email)

        message = ('Please check the email you registered with for a'
                  ' verification email.')
        response = {'data': {
            'created': True,
            'message': message
        }}
        headers = {'Location': url_for('AuthView:post')}
        return response, 201, headers

    @route('/activate_account/<activation_token>', methods=['GET'])
    def activate_account(self, username):
        response = {'data': {
            'activated': True,
            'message': 'Your account has been activated.'
        }}
        headers = {'Location': url_for('AuthView:post')}
        return response, 200, headers
