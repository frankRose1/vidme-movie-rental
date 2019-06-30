import datetime

from vidme.blueprints.billing.models.credit_card import CreditCard
from vidme.blueprints.billing.models.invoice import Invoice


class TestCreditCard(object):
    def test_credit_card_expiring_soon(self):
        """Credit card is expring soon"""
        may_29_2019 = datetime.date(2019, 5, 29)
        exp_dates = (
            datetime.date(2000, 1, 1),
            datetime.date(2019, 6, 3),
            datetime.date(2019, 7, 1)
        )

        for date in exp_dates:
            assert CreditCard.is_expiring_soon(may_29_2019, date)

    def test_credit_card_not_expiring_soon(self):
        """ CreditCard is not expring soon """
        may_29_2019 = datetime.date(2019, 5, 29)
        exp_dates = (
            datetime.date(2019, 8, 28),
            datetime.date(2020, 1, 1),
            datetime.date(2020, 5, 29)
        )

        for date in exp_dates:
            assert CreditCard.is_expiring_soon(may_29_2019, date) is False


class TestInvoice(object):
    def test_parse_payload_from_event(self, mock_stripe):
        """Parse the correct data from a Stripe event payload"""
        event_payload = {
            'created': 1326853478,
            'livemode': False,
            'id': 'evt_000',
            'type': 'invoice.created',
            'object': 'event',
            'request': None,
            'pending_webhooks': 1,
            'api_version': '2016-03-07',
            'data': {
                'object': {
                    'date': 1433018770,
                    'id': 'in_000',
                    'period_start': 1433018770,
                    'period_end': 1433018770,
                    'lines': {
                        'data': [
                            {
                                'id': 'sub_000',
                                'object': 'line_item',
                                'type': 'subscription',
                                'livemode': True,
                                'amount': 0,
                                'currency': 'usd',
                                'proration': False,
                                'period': {
                                    'start': 1433162255,
                                    'end': 1434371855
                                },
                                'subscription': None,
                                'quantity': 1,
                                'plan': {
                                    'interval': 'month',
                                    'name': 'Gold',
                                    'created': 1424879591,
                                    'amount': 500,
                                    'currency': 'usd',
                                    'id': 'gold',
                                    'object': 'plan',
                                    'livemode': False,
                                    'interval_count': 1,
                                    'trial_period_days': 14,
                                    'nickname': 'Gold',
                                    'product': 'prod_000',
                                    'metadata': {},
                                    'statement_descriptor': 'GOLD MONTHLY'
                                },
                                'description': None,
                                'discountable': True,
                                'metadata': {}
                            }
                        ],
                        'total_count': 1,
                        'object': 'list',
                        'url': '/v1/invoices/in_000/lines'
                    },
                    'subtotal': 0,
                    'total': 500,
                    'customer': 'cus_000',
                    'object': 'invoice',
                    'attempted': False,
                    'closed': True,
                    'forgiven': False,
                    'paid': True,
                    'livemode': False,
                    'attempt_count': 0,
                    'amount_due': 0,
                    'currency': 'usd',
                    'starting_balance': 0,
                    'ending_balance': 0,
                    'next_payment_attempt': None,
                    'webhooks_delivered_at': None,
                    'charge': None,
                    'discount': None,
                    'application_fee': None,
                    'subscription': 'sub_000',
                    'tax_percent': None,
                    'tax': None,
                    'metadata': {},
                    'statement_descriptor': None,
                    'description': None,
                    'receipt_number': '0009000'
                }
            }
        }

        parsed_payload = Invoice.parse_from_event(event_payload)

        assert parsed_payload['payment_id'] == 'cus_000'
        assert parsed_payload['plan'] == 'Gold'
        assert parsed_payload['receipt_number'] == '0009000'
        assert parsed_payload['description'] == 'GOLD MONTHLY'
        assert parsed_payload['period_start_on'] == datetime.date(2015, 6, 1)
        assert parsed_payload['period_end_on'] == datetime.date(2015, 6, 15)
        assert parsed_payload['currency'] == 'usd'
        assert parsed_payload['tax'] is None
        assert parsed_payload['tax_percent'] is None
        assert parsed_payload['total'] == 500

    def test_invoice_upcoming(self, mock_stripe):
        """Parse the correct data from a Stripe invoice payload"""
        parsed_payload = Invoice.upcoming('cus_000')
        next_bill_on = datetime.datetime(2015, 5, 30, 20, 46, 10)

        assert parsed_payload['plan'] == 'Gold'
        assert parsed_payload['description'] == 'GOLD MONTHLY'
        assert parsed_payload['next_bill_on'] == next_bill_on
        assert parsed_payload['amount_due'] == 500
        assert parsed_payload['interval'] == 'month'
