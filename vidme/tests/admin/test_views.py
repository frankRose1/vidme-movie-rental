import datetime

import pytz
from flask import url_for

from lib.tests import ViewTestMixin, assert_status_with_message
from vidme.blueprints.user.models import User


class TestDashboardView(ViewTestMixin):
    def test_get_dashboard(self, subscriptions):
        """
        Should return grouped data regarding number of users and subscriptions in the
        system
        """
        self.authenticate()
        response = self.client.get(url_for('AdminView:index'))
        data = response.get_json()['data']
        plans_group = data['group_and_count_plans']
        users_group = data['group_and_count_users']

        assert response.status_code == 200
        # type of subscriptions in the DB and their respective totals
        assert plans_group['query'][0][0] == 1
        assert plans_group['query'][0][1] == 'gold'
        assert plans_group['total'] == 1
        # type of user(admin or member) and the respective totals
        assert users_group['query'][0][0] == 1
        assert users_group['query'][0][1] == 'admin'
        assert users_group['query'][1][0] == 1
        assert users_group['query'][1][1] == 'member'
        assert users_group['total'] == 2


class TestCancelSubscription(ViewTestMixin):
    def test_user_not_found(self):
        """Return a 404 if a user doesn't exist"""
        self.authenticate()
        response = self.client.delete(url_for('AdminView:cancel_subscription',
                                      username='iDontExist1'))
        assert response.status_code == 404
        assert response.get_json()['error'] == 'User not found.'

    def test_no_existing_subscription(self):
        """Return a 400 if a user doesn't have a subscription"""
        self.authenticate()
        response = self.client.delete(url_for('AdminView:cancel_subscription',
                                      username='testAdmin1'))
        error = 'testAdmin1 doesn\'t have an active subscription.'
        assert response.status_code == 400
        assert response.get_json()['error'] == error    

    def test_cancel_subscription(self, subscriptions, mock_stripe):
        """Successfully cancel a user's subscription"""
        self.authenticate()
        response = self.client.delete(url_for('AdminView:cancel_subscription',
                                      username='firstSub1'))
        data = response.get_json()['data']

        assert response.status_code == 200
        assert data['deleted'] is True
        assert data['message'] == 'User\'s subscription has been cancelled.'

        user = User.find_by_identity('firstSub1')
        assert user.subscription is None
        assert user.cancelled_subscription_on <= datetime.datetime.now(pytz.utc)


class TestEditUser(ViewTestMixin):
    def test_user_not_found(self):
        """Return a 404 if a user doesn't exist"""
        self.authenticate()
        response = self.client.put(url_for('AdminView:edit_user',
                                      username='iDontExist1'))
        assert response.status_code == 404
        assert response.get_json()['error'] == 'User not found.'

    def test_invalid_data(self):
        """Return a 400 if no json data is sent in the request"""
        self.authenticate()
        response = self.client.put(url_for('AdminView:edit_user',
                                      username='testAdmin1'))
        assert response.status_code == 400
        assert response.get_json()['error'] == 'Invalid input.'

    def test_invalid_role(self):
        """Return a 422 if role fails schema validation"""
        self.authenticate()
        data = {
            'role': 'superAdmin',
            'username': 'testAdmin1'
        }
        response = self.client.put(url_for('AdminView:edit_user',
                                      username='testAdmin1'), json=data)
        error = 'superAdmin is not a valid role.'
        assert response.status_code == 422
        assert response.get_json()['error']['role'][0] == error

    def test_invalid_username(self):
        """Return a 422 if username fails schema validation"""
        self.authenticate()
        data = {
            'role': 'admin',
            'username': 'Spaces not allowed *&'
        }
        response = self.client.put(url_for('AdminView:edit_user',
                                      username='testAdmin1'), json=data)
        error = 'Username must be letters, numbers and underscores only.'
        assert response.status_code == 422
        assert response.get_json()['error']['username'][0] == error

    def test_last_admin_in_system(self):
        """
        Cant change a users role if the user is the last admin in the system.
        """
        self.authenticate()
        data = {
            'role': 'member',
            'username': 'testAdmin1'
        }
        response = self.client.put(url_for('AdminView:edit_user',
                                      username='testAdmin1'), json=data)
        error = 'User is the last admin in the system.'
        assert response.status_code == 400
        assert response.get_json()['error'] == error

    def test_username_is_unique(self, subscriptions):
        """If username is being changed, make sure its not already taken"""
        self.authenticate()
        data = {
            'role': 'admin',
            'username': 'firstSub1' # this username exists from subscriptions
        }
        response = self.client.put(url_for('AdminView:edit_user',
                                      username='testAdmin1'), json=data)
        assert response.status_code == 400
        assert response.get_json()['error'] == 'Username is already taken.'

    def test_edit_user(self, subscriptions):
        """Successfully update a user account and set location headers"""
        self.authenticate()
        data = {
            'role': 'admin',
            'username': 'firstSub1'
        }
        response = self.client.put(url_for('AdminView:edit_user',
                                      username='firstSub1'), json=data)
        location = response.headers['Location']
        assert response.status_code == 204
        assert location == url_for('AdminView:get_user', username='firstSub1')

        user = User.find_by_identity('firstSub1')
        assert user.role == 'admin'


class TestGetUser(ViewTestMixin):
    def test_user_not_found(self):
        """Return a 404 for a user that doesn't exist"""
        self.authenticate()
        response = self.client.get(url_for('AdminView:get_user',
                                           username='iDontExist'))
        assert response.status_code == 404
        assert response.get_json()['error'] == 'User not found.'
    
    def test_get_user_with_subscription(self, subscriptions):
        """
        Return the user's data and the upcoming invoice data if the user is
        currently subscribed
        """
        self.authenticate()
        response = self.client.get(url_for('AdminView:get_user',
                                           username='firstSub1'))
        data = response.get_json()['data']
        user = data['user']
        upcoming_invoice = data['upcoming_invoice']
        assert response.status_code == 200
        assert 'password' not in user
        assert user['username'] == 'firstSub1'
        assert 'sign_in_count' in user
        assert 'created_on' in user
        assert 'updated_on' in user
        assert 'credit_card' in user
        assert 'subscription' in user
        assert 'name' in user
        assert 'email' in user
        assert 'last_sign_in_ip' in user
        assert 'current_sign_in_ip' in user
        assert 'last_sign_in_on' in user
        assert 'current_sign_in_on' in user

        assert upcoming_invoice['interval'] == 'month'
        assert upcoming_invoice['amount_due'] == 500
        assert upcoming_invoice['description'] == 'GOLD MONTHLY'
        assert upcoming_invoice['plan'] == 'Gold'

    def test_get_user_no_subscription(self, invoices):
        """
        Return the user's data including invoices(billing) data, even if
        the user is not currently subscribed
        """
        self.authenticate()
        response = self.client.get(url_for('AdminView:get_user',
                                           username='testAdmin1'))
        data = response.get_json()['data']
        user = data['user']
        invoices = data['invoices']

        assert response.status_code == 200
        assert data['upcoming_invoice'] is None
        assert len(invoices) == 2
        assert user['sign_in_count'] >= 1
        assert 'password' not in 'user'
        assert user['username'] == 'testAdmin1'
        assert 'created_on' in user
        assert 'updated_on' in user
        assert 'credit_card' in user
        assert 'subscription' in user
        assert 'name' in user
        assert 'email' in user
        assert 'last_sign_in_ip' in user
        assert 'current_sign_in_ip' in user
        assert 'last_sign_in_on' in user
        assert 'current_sign_in_on' in user


class TestGetUsers(ViewTestMixin):
    def test_get_users(self):
        """Return a list of users in the DB"""
        self.authenticate()
        response = self.client.get(url_for('AdminView:users'))
        data = response.get_json()['data']
        users = data['users']

        assert response.status_code == 200
        assert data['has_next'] is False
        assert data['has_prev'] is False
        assert data['next_num'] is None
        assert data['prev_num'] is None
        assert 'password' not in users[0]
        assert 'username' in users[0]
        assert 'email' in users[0]
        assert 'role' in users[0]
        assert 'sign_in_count' in users[0]
        assert 'last_sign_in_on' in users[0]
        assert 'payment_id' in users[0]

    def test_search_option(self):
        """AdminView:users supports a search feature"""
        self.authenticate()
        args = {'q': 'noResultsUsername'}
        response = self.client.get(url_for('AdminView:users'),
                                   query_string=args)
        data = response.get_json()['data']

        assert response.status_code == 200
        assert len(data['users']) == 0
        assert data['has_next'] is False
        assert data['has_prev'] is False
        assert data['next_num'] is None
        assert data['prev_num'] is None