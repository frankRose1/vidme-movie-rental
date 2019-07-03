from flask import url_for

from lib.tests import ViewTestMixin, assert_status_with_message


class TestCreateSubscription(ViewTestMixin):
    def test_subscription_already_exists(self, subscriptions):
        """User already has an active subscription"""
        self.authenticate(identity='subscriber@local.host')
        data = {
            'stripe_token': 'tok_visa',
            'customer_name': 'Subby',
            'plan': 'gold'
        }
        response = self.client.post(
            url_for('SubscriptionsView:post'), json=data)
        assert_status_with_message(
            400, response, 'You already have an active subscription.')

    def test_invalid_customer_name(self):
        """Missing customer name fails schema validation"""
        self.authenticate()
        data = {
            'customer_name': '',
            'plan': 'gold',
            'stripe_token': 'tok_visa'
        }
        response = self.client.post(
            url_for('SubscriptionsView:post'), json=data)
        assert response.status_code == 422

    def test_invalid_stripe_token(self):
        """Missing stripe token fails schema validation"""
        self.authenticate()
        data = {
            'stripe_token': '',
            'customer_name': 'Jane Smith',
            'plan': 'gold',
        }
        response = self.client.post(
            url_for('SubscriptionsView:post'), json=data)
        assert response.status_code == 422

    def test_invalid_plan(self):
        """Missing plan fails schema validation"""
        self.authenticate()
        data = {
            'plan': '',
            'stripe_token': 'tok_visa',
            'customer_name': 'Jane Smith',
        }
        response = self.client.post(
            url_for('SubscriptionsView:post'), json=data)
        assert response.status_code == 422

    def test_plan_not_found(self):
        """Plan that doesn't exist returns a 404"""
        self.authenticate()
        data = {
            'plan': 'iDontExist',
            'stripe_token': 'tok_visa',
            'customer_name': 'Jane Smith',
        }
        response = self.client.post(
            url_for('SubscriptionsView:post'), json=data)
        assert_status_with_message(404, response, 'Plan not found.')


class TestUpdateSubscription(ViewTestMixin):
    def test_credit_card_not_found(self):
        """
        If a user is currently subbed, a CC would be in the DB. If no CC is
        related to the authenticated user, return a 404
        """
        self.authenticate()
        data = {
            'stripe_token': 'tok_visa',
            'customer_name': 'Jane Smith',
        }
        response = self.client.put(
            url_for('SubscriptionsView:put'), json=data)
        assert_status_with_message(
            404, response, 'You do not have a payment method on file.')

    def test_missing_required_fields(self, subscriptions):
        """Missing stripe_token and customer name"""
        self.authenticate(identity='subscriber@local.host')
        data = {'stripe_token': '', 'customer_name': ''}
        response = self.client.put(
            url_for('SubscriptionsView:put'), json=data)
        assert response.status_code == 422


class TestGetSubscription(ViewTestMixin):
    def test_billing_info_no_credit_card(self):
        """Should return a 404 if no CC is on file"""
        self.authenticate()
        response = self.client.get(url_for('SubscriptionsView:index'))
        assert_status_with_message(404, response,
                                   'No credit card information was found.')

    def test_billing_info(self, subscriptions):
        self.authenticate(identity='subscriber@local.host')
        response = self.client.get(url_for('SubscriptionsView:index'))
        data = response.get_json()['data']
        plan = data['active_plan']
        card = data['credit_card']

        assert response.status_code == 200
        assert plan['amount'] == 999
        assert plan['currency'] == 'usd'
        assert plan['id'] == 'gold'
        assert plan['statement_descriptor'] == 'VIDME GOLD'
        assert plan['interval'] == 'month'
        assert card['last4'] == 4242
        assert card['brand'] == 'Visa'
        assert 'is_expiring' in card
        assert 'exp_date' in card
        assert 'updated_on' in card
        assert 'created_on' in card


class TestCancelSubscription(ViewTestMixin):
    def test_no_active_subscription(self):
        """
        A user with no active subscription should not be able to access the
        delete resource
        """
        self.authenticate()
        response = self.client.delete(url_for('SubscriptionsView:delete'))
        msg = 'You need an active subscription to access this resource.'
        assert_status_with_message(403, response, msg)

    def test_cancel_subscription(self, subscriptions, mock_stripe):
        """Successfully cancels a user's subscription"""
        self.authenticate(identity='subscriber@local.host')
        response = self.client.delete(url_for('SubscriptionsView:delete'))
        assert response.status_code == 204
