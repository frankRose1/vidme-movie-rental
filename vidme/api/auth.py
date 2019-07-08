from flask import jsonify, request
from flask_classful import FlaskView

from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    set_access_cookies,
    unset_jwt_cookies
)

from vidme.blueprints.user.models import User
from vidme.blueprints.user.schemas import auth_schema


class AuthView(FlaskView):
    route_prefix = '/api'

    def post(self):
        json_data = request.get_json()

        if not json_data:
            response = jsonify({
                'error': 'Invalid input.'
            })
            return response, 400

        data, errors = auth_schema.load(json_data)

        if errors:
            response = jsonify({
                'error': errors
            })

            return response, 422

        user = User.find_by_identity(data['identity'])

        if user and user.authenticated(password=data['password']):
            if user.is_active():
                # identity is used to lookup a user on protected endpoints
                access_token = create_access_token(identity=user.username)

                user.update_activity_tracking(request.remote_addr)

                response = jsonify({
                    'data': {
                        'access_token': access_token
                    }
                })

                # Set the JWTs and the CSRF double submit protection cookies
                # Clients such as web browsers support cookies and
                # "set_access_cookies" will set two cookies in the browser,
                # 1)access_token 2)CSRF token
                set_access_cookies(response, access_token)

                return response, 200
            else:
                error = ('This account is not active. If you recently signed'
                        ' up for an account, check your email for a'
                        ' verification link.')
                return {'error': error}, 400

        response = jsonify({
            'error': 'Invalid credentials.'
        })
        return response, 401

    @jwt_required
    def delete(self):
        response = jsonify({
            'data': {
                'logout': True
            }
        })

        # Since our api also accepts cookies, the backend needs to send a
        # response to delete the cookies. unset_jwt_cookies will remove the
        # cookies in the users browser
        unset_jwt_cookies(response)

        return response, 200
