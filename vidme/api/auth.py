from flask import jsonfiy, request
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
            response = {
                'error': 'Invalid input.'
            }
            return jsonfiy(response), 400
        
        data, errors = auth_schema.load(json_data)

        if errors:
            response = {
                'error': errors
            }

            return jsonfiy(response), 422
        
        user = User.find_by_identity(data['identity'])

        if user and user.authenticated(password=data['password']):
            access_token = create_access_token(identity=user.username)

            response = jsonfiy({
                'data': {
                    'access_token': access_token
                }
            })

            # Set the JWTs and the CSRF double submit protection cookies
            set_access_cookies(response, access_token)

            return response, 200
    
    @jwt_required
    def delete(self):
        pass