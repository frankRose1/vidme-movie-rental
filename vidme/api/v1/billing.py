from flask import (
    request,
    jsonify,
    url_for
)
from flask_jwt_extended import jwt_required, current_user

from vidme.api.v1 import V1FlaskView
from vidme.blueprints.billing.models.subscription import Subscription
from vidme.blueprints.billing.schemas import (
    create_edit_subscription_schema,
    billing_info_schema
)
from lib.decorators import handle_stripe_exceptions, subscription_required


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
        json_data = request.get_json()
        data, errors = create_edit_subscription_schema.load(json_data)

        if errors:
            return jsonify({'error': errors}), 422

        # get the subscription plan, send a 404 if it doesnt exist
        subscription_plan = Subscription.get_plan(data['plan'])
        if subscription_plan is None:
            response: {'error': 'Plan not found.'}
            return jsonify(response), 404

        # if data is valid create a subscription
        subscription = Subscription()
        subscription.create(user=current_user,
                            name=data['customer_name'],
                            plan=data['plan'],
                            token=data['stripe_token'])

        return jsonify({}), 201

    @handle_stripe_exceptions
    @jwt_required
    def put(self):
        """Users should be able to update billing info without interuption"""
        # if a user had subscribed to a plan they would have
        # a CC model relationship
        if not current_user.credit_card:
            response = {
                'error': 'You do not have a payment method on file.'
            }
            return jsonify(response), 404

        # validate incoming data
        json_data = request.get_json()
        data, errors = create_edit_subscription_schema.load(json_data)

        if errors:
            response = {'error': errors}
            return jsonify(response), 422

        card = current_user.credit_card

        # @handle_stripe_exceptions will catch any stripe errors that may
        # occur in update_payment_method
        subscription = Subscription()
        subscription.update_payment_method(user=current_user,
                                           credit_card=card,
                                           name=data['customer_name'],
                                           token=data['stripe_token'])
        return jsonify({}), 200

    @jwt_required
    def index(self):
        """
        Get the current users billing info, good for pre-populating the
        update form
        """
        if not current_user.credit_card:
            response = {
                'error': 'No credit card information was found.'
            }
            return jsonify(response), 404

        active_plan = Subscription.get_plan(current_user.subscription.plan)
        billing_info = billing_info_schema.dump(current_user.credit_card)
        response = {'data': {
            'billing_info': billing_info.data,
            'active_plan': active_plan
        }}
        return jsonify(response), 200

    @handle_stripe_exceptions
    @subscription_required
    @jwt_required
    def delete(self):
        """Cancel a user's subscription."""
        subscription = Subscription()
        subscription.cancel(user=current_user)

        # TODO set headers to url_for("SubscriptionView:post")
        return jsonify({}), 204


class PlanView(V1FlaskView):

    def index(self):
        """Show all of the available plans?"""
        plans = Subscription.get_all_plans()
        response = {'data': {
            'plans': plans
        }}
        return jsonify(response), 200

    @handle_stripe_exceptions
    @subscription_required
    @jwt_required
    def put(self):
        """
        Update a plan
        """
        # get the new plan from the client, token and customer name are not
        # needed since that information is already set up
        json_data = request.get_json()
        partials = ('stripe_token', 'customer_name')
        data, errors = create_edit_subscription_schema.load(json_data,
                                                            partial=partials)
        if errors:
            response = {'error': errors}
            return jsonify(response), 422
        # plan should be bronze, gold, or platinum
        new_plan = Subscription.get_plan(data['plan'])
        if new_plan is None:
            response = {'error': 'Plan not found.'}
            return jsonify(response), 404

        current_plan = current_user.subscription.plan
        if current_plan == data['plan']:
            response = {
                'error': 'New plan can\'t be the same as your old plan'}
            return jsonify(response), 400

        subscription = Subscription()
        subscription.update(user=current_user, plan=data['plan'])
        # TODO set headers url_for("SubscriptionView:index")
        return jsonify({}), 204
