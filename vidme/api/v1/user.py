from flask import request, url_for

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

        headers = {'Location': url_for('AuthView:post')}
        return '', 201, headers
