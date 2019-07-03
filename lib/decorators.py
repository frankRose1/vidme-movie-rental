from functools import wraps

import stripe
from flask import jsonify
from flask_jwt_extended import (
    verify_jwt_in_request,
    get_jwt_claims,
    current_user
)


def admin_required(fn):
    """
    Will protect endpoints to make sure that 1) a valid JWT is provided, and
    2) the user has a role of admin. 

    :param fn: Function being wrapped
    :type fn: Function

    :return: Wrapper function
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()  # will return a 401 if no token provided
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


def jwt_and_subscription_required(fn):
    """
    Ensures a user is authenticated and has an active subscription before
    accessing certain endpoints.

    :param fn: Function being decorated
    :type fn: Function
    :return: Function
    """
    @wraps(fn)
    def decorated_function(*args, **kwargs):
        verify_jwt_in_request()
        if not current_user.subscription:
            msg = 'You need an active subscription to access this resource.'
            response = {
                'error': msg
            }
            return jsonify(response), 403
        return fn(*args, **kwargs)

    return decorated_function


def handle_stripe_exceptions(fn):
    """
    The stripe API can throw many different errors regarding the user's
    CC/billing info. This decorator will handle various exceptions and provide
    a more informative response to the client, rather than returning a 500.

    :param fn: Function being wrapped
    :type fn: Function

    :return: Function
    """
    @wraps(fn)
    def decorated_function(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except stripe.error.CardError:
            response: {
                'error': 'Sorry your card was declined. Try again perhaps?'
            }
            return jsonify(response), 400
        except stripe.error.InvalidRequestError as e:
            return jsonify({'error': e}), 400
        except stripe.error.AuthenticationError:
            response = {
                'error': 'Authentication with our payment gateway failed.'
            }
            return jsonify(response), 400
        except stripe.error.APIConnectionError:
            response = {
                'error': 'Our payment gateway is experiencing connectivity issues, please try again.'
            }
            return jsonify(response), 400
        except stripe.error.StripeError:
            response = {
                'error': 'Our payment gateway is having issues, please try again.'
            }
            return jsonify(response), 400

    return decorated_function
