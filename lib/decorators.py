from functools import wraps

from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_claims

def admin_required(fn):
    """
    Will protect endpoints to make sure that 1) a valid JWT is provided, and
    2) the user has a role of admin. 

    :param fn: Endpoint being wrapped
    :return: Wrapper function
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request() # will return a 401 if no token provided
        claims = get_jwt_claims()
        if claims['role'] != 'admin':
            response = {
                'error': {
                    'message': 'Admin required.'
                }
            }
            return jsonify(response), 403
        else:
            return fn(*args, **kwargs)
    return wrapper
