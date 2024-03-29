from flask import (
    request,
    url_for
)
from flask_jwt_extended import jwt_required, current_user
from marshmallow import ValidationError

from vidme.api import JSONViewMixin
from vidme.api.v1 import V1FlaskView
from vidme.blueprints.billing.models.subscription import Subscription
from vidme.blueprints.billing.models.invoice import Invoice
from vidme.blueprints.billing.schemas import (
    create_edit_subscription_schema,
    credit_card_schema,
    invoices_schema
)
from lib.decorators import (
    handle_stripe_exceptions,
    jwt_and_subscription_required
)


class SubscriptionsView(JSONViewMixin, V1FlaskView):

    @jwt_required
    @handle_stripe_exceptions
    def post(self):
        if current_user.subscription:
            response = {
                'error': 'You already have an active subscription.'
            }
            return response, 400

        # validate the incoming data
        json_data = request.get_json()

        if not json_data:
            response = {'error': 'Invalid input.'}
            return response, 400

        try:
            data = create_edit_subscription_schema.load(json_data)
        except ValidationError as err:
            return {'error': err.messages}, 422

        # get the subscription plan, send a 404 if it doesnt exist
        subscription_plan = Subscription.get_plan(data['plan'])
        if subscription_plan is None:
            response = {'error': 'Plan not found.'}
            return response, 404

        # if data is valid create a subscription
        subscription = Subscription()
        subscription.create(user=current_user,
                            name=data['customer_name'],
                            plan=data['plan'],
                            token=data['stripe_token'])

        headers = {'Location': url_for('SubscriptionsView:index')}
        return '', 201, headers

    @jwt_required
    @handle_stripe_exceptions
    def put(self):
        """Users should be able to update billing info without interruption"""
        # if a user had subscribed to a plan they would have
        # a CC model relationship
        if not current_user.credit_card:
            response = {
                'error': 'You do not have a payment method on file.'
            }
            return response, 404

        json_data = request.get_json()

        if not json_data:
            response = {'error': 'Invalid input.'}
            return response, 400

        try:
            data= create_edit_subscription_schema.load(json_data,
                                                       partial=('plan',))
        except ValidationError as err:
            response = {'error': err.messages}
            return response, 422

        card = current_user.credit_card

        # @handle_stripe_exceptions will catch any stripe errors that may
        # occur in update_payment_method
        subscription = Subscription()
        subscription.update_payment_method(user=current_user,
                                           credit_card=card,
                                           name=data['customer_name'],
                                           token=data['stripe_token'])

        headers = {'Location': url_for('SubscriptionsView:index')}
        return '', 204, headers

    @jwt_required
    def index(self):
        """ Get the current users CC and current plan info """
        if not current_user.credit_card:
            response = {
                'error': 'No credit card information was found.'
            }
            return response, 404

        active_plan = Subscription.get_plan(current_user.subscription.plan)
        credit_card = credit_card_schema.dump(current_user.credit_card)
        response = {'data': {
            'credit_card': credit_card,
            'active_plan': active_plan
        }}
        return response, 200

    @jwt_and_subscription_required
    @handle_stripe_exceptions
    def delete(self):
        """Cancel a user's subscription."""
        subscription = Subscription()
        subscription.cancel(user=current_user)

        headers = {'Location': url_for('SubscriptionsView:post')}
        return '', 204, headers


class PlansView(JSONViewMixin, V1FlaskView):

    def index(self):
        """Show all of the available plans"""
        plans = Subscription.get_all_plans()
        response = {'data': {
            'plans': plans
        }}
        return response, 200

    @jwt_and_subscription_required
    @handle_stripe_exceptions
    def put(self):
        """
        Update a plan
        """
        # get the new plan from the client, token and customer name are not
        # needed since that information is already set up
        json_data = request.get_json()

        if not json_data:
            response = {'error': 'Invalid input.'}
            return response, 400

        partials = ('stripe_token', 'customer_name',)
        try:
            data = create_edit_subscription_schema.load(json_data,
                                                        partial=partials)
        except ValidationError as err:
            response = {'error': err.messages}
            return response, 422

        # plan should be bronze, gold, or platinum
        new_plan = Subscription.get_plan(data['plan'])
        if new_plan is None:
            response = {'error': 'Plan not found.'}
            return response, 404

        current_plan = current_user.subscription.plan
        if current_plan == data['plan']:
            response = {
                'error': 'New plan can\'t be the same as your old plan.'
            }
            return response, 400

        subscription = Subscription()
        subscription.update(user=current_user, plan=data['plan'])

        headers = {'Location': url_for('SubscriptionsView:index')}
        return '', 204, headers


class InvoicesView(JSONViewMixin, V1FlaskView):
    @jwt_required
    @handle_stripe_exceptions
    def index(self):
        """
        Return the user's previous invoices, and the upcoming invoice
        (provided by Stripe). Upcoming invoice could be null if a user has
        unsubbed.
        """
        invoices = Invoice.billing_history(user=current_user)

        if current_user.subscription:
            # get the upcoming invoice from stripe
            upcoming_invoice = Invoice.upcoming(
                customer_id=current_user.payment_id)
        else:
            upcoming_invoice = None

        dumped_invoices = invoices_schema.dump(invoices)
        response = {'data': {
            'invoices': dumped_invoices,
            'upcoming_invoice': upcoming_invoice
        }}

        return response, 200
