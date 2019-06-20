from flask import (
    request,
    jsonify,
    url_for
)
from flask_jwt_extended import jwt_required, current_user

from vidme.api.v1 import V1FlaskView
from vidme.blueprints.billing.models.subscription import Subscription
from vidme.blueprints.billing.schemas import credit_card_schema
from lib.decorators import handle_stripe_exceptions


class SubscriptionView(V1FlaskView):

    @handle_stripe_exceptions
    @jwt_required
    def post(self):
        if current_user.subscription:
            response = {
                'error': 'You already have an active subscription.'
            }
            return jsonify(response), 400

        # validate the incoming data
        data, errors = credit_card_schema.load(request.get_json())

        if errors:
            return jsonify({'error': errors}), 422

        # get the subscription plan, send a 404 if it doesnt exist
        subscription_plan = Subscription.get_plan(data['plan'])
        if subscription_plan is None:
            response: {'error': 'Plan not found.'}
            return jsonify(response), 404

        # if data is valid create a subscription
        subscription = Subscription()
        created = subscription.create(user=current_user,
                                      name=data['customer_name'],
                                      plan=data['plan'],
                                      token=data['stripe_token'])

        return jsonfiy({}), 201

    @handle_stripe_exceptions
    @jwt_required
    def put(self):
        """Users should be able to update billing info without interuption"""
        # if a user had subscribed to a plan they would have
        #  a CC model relationship
        if not current_user.credit_card:
            response = {
                'error': 'No credit card information was found.'
            }
            return jsonify(response), 404

        active_plan = Subscription.get_plan(current_user.subscription.plan)

        card = current_user.credit_card

        # validate incoming data
        data, errors = credit_card_schema.load(request.get_json())

        # @handle_stripe_exceptions will catch any stripe errors that may
        # occur in update_payment_method
        subscription = Subscription()
        updated = subscription.update_payment_method(user=current_user,
                                                     credit_card=card,
                                                     name=data['customer_name'],
                                                     token=data['stripe_token'])
        return {}, 200

    @jwt_required
    def get(self):
        """
        Get the current users billing info, good for pre-populating the
        update form
        """
        if not current_user.credit_card:
            response = {
                'error': 'No credit card information was found.'
            }
            return jsonify(response), 404
