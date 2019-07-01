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
        """Successfully update a user account"""
        self.authenticate()
        data = {
            'role': 'admin',
            'username': 'firstSub1'
        }
        response = self.client.put(url_for('AdminView:edit_user',
                                      username='firstSub1'), json=data)
        location = response.headers['Location']
        assert response.status_code == 400