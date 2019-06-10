from flask import jsonify, request

from vidme.api.v1 import V1FlaskView
from vidme.blueprints.user.models import User
from vidme.blueprints.user.schemas import registration_schema


class UsersView(V1FlaskView):
    def post(self):
        json_data = request.get_json()

        if not json_data:
            response = jsonify({'error': 'Invalid input.'})
            return response, 400

        data, errors = registration_schema.load(json_data)

        if errors:
            response = jsonify({
                'error': errors
            })

            return response, 422

        user = User()
        user.email = data.get('email')
        user.username = data.get('username')
        user.password = User.encrypt_password(data.get('password'))
        user.save()

        return jsonify(data), 201
