from flask import request, jsonify
from flask_classful import FlaskView
from stripe.error import InvalidRequestError

from vidme.blueprints.billing.models.invoice import Invoice
from vidme.blueprints.billing.gateways.stripecom import Event as \
    PaymentEvent


class StripeWebhookView(FlaskView):
    """
    When a user subscribes to a plan, stripe will create an invoice for a user
    and will continue to create invoices for every billing cycle that a user
    is subscribed to a plan. Using webhooks, the API can listen for the
    "invoice.created" event and save an invoice locally, which allows the
    client to display a user's billing history easily.
    """
    route_prefix = '/api'

    def post(self):
        """
        This endpoint exposes the API to stripe to fulfill webhook events.
        """
        json_data = request.json

        if not json_data:
            response = jsonify({'error': 'Invalid input.'})
            return response, 400

        webhook_id = json_data.get('id')
        if webhook_id is None:
            response = jsonify({'error': 'Invalid stripe event.'})
            return response, 400

        try:
            safe_event = PaymentEvent.retrieve(webhook_id)
            parsed_event = Invoice.parse_from_event(safe_event)

            Invoice.prepare_and_save(parsed_event)
        except InvalidRequestError as e:
            # could not parse the event
            return jsonify({'error': str(e)}), 422
        except Exception as e:
            # In this case something went really wrong so send a 200 so that
            # stripe stops trying to fulfill this webhook request
            return jsonify({'error': str(e)}), 200

        return jsonify({'success': True}), 200
