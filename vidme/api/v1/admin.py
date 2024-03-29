from flask import request, url_for
from flask_classful import route
from flask_jwt_extended import current_user
from marshmallow import ValidationError
from sqlalchemy import text

from vidme.api import JSONViewMixin
from vidme.api.v1 import V1FlaskView
from vidme.blueprints.admin.models import Dashboard
from lib.decorators import admin_required, handle_stripe_exceptions
from vidme.blueprints.billing.models.subscription import Subscription
from vidme.blueprints.billing.models.invoice import Invoice
from vidme.blueprints.user.models import User
from vidme.blueprints.admin.schemas import (
    admin_edit_user_schema,
    users_schema,
    user_detail_schema,
    bulk_delete_schema
)
from vidme.blueprints.billing.schemas import invoices_schema

USER_NOT_FOUND = 'User not found.'


class AdminView(JSONViewMixin, V1FlaskView):

    @admin_required
    def index(self):
        """
        Count and group(by role) all users and subscriptions in the system.
        Will show a total and allow the client to calculate percentages
        (e.g which percent of users are members vs admin).
        """
        group_and_count_users = Dashboard.group_and_count_users()
        group_and_count_plans = Dashboard.group_and_count_plans()
        response = {'data': {
            'group_and_count_users': group_and_count_users,
            'group_and_count_plans': group_and_count_plans
        }}
        return response

    @route('/cancel_subscription/<username>', methods=['DELETE'])
    @admin_required
    @handle_stripe_exceptions
    def cancel_subscription(self, username):
        """Admins can canel a user's subscription"""

        user = User.find_by_identity(username)

        if user is None:
            response = {'error': USER_NOT_FOUND}
            return response, 404

        if not user.subscription:
            error = '{0} doesn\'t have an active subscription.'.format(
                     username)
            response = {
                'error': error
            }
            return response, 400

        subscription = Subscription()
        subscription.cancel(user=user)
        response = {'data': {
            'deleted': True,
            'message': 'User\'s subscription has been cancelled.'
        }}
        return response, 200

    @route('/users', methods=['GET'])
    @admin_required
    def users(self):
        """
        Use pagination to list out users in the database
        """
        page = request.args.get('page', 1)
        page_size = request.args.get('page_size', 30)

        # return 30 users at a time max
        if page_size > 30:
            page_size = 30

        sort_by = User.sort_by(request.args.get('sort', 'created_on'),
                               request.args.get('direction', 'desc'))
        order_values = '{0} {1}'.format(sort_by[0], sort_by[1])

        # a search feature is provided if the client wants to implement one
        # thats what request.args.get('q') is
        paginated_users = User.query \
            .filter(User.search(request.args.get('q', text('')))) \
            .order_by(User.role.asc(), User.payment_id, text(order_values)) \
            .paginate(page, page_size, True)

        dumped_users = users_schema.dump(paginated_users.items)
        response = {'data': {
            'users': dumped_users,
            'has_next': paginated_users.has_next,
            'has_prev': paginated_users.has_prev,
            'prev_num': paginated_users.prev_num,
            'next_num': paginated_users.next_num,
        }}
        return response

    @route('/users/<username>', methods=['GET'])
    @admin_required
    @handle_stripe_exceptions
    def get_user(self, username):
        """Allows an admin to fetch specific user data
        """
        user = User.find_by_identity(username)

        if user is None:
            response = {'error': USER_NOT_FOUND}
            return response, 404

        invoices = Invoice.billing_history(user=user)
        if user.subscription:
            # get the upcoming invoice from Stripe
            upcoming = Invoice.upcoming(customer_id=user.payment_id)
        else:
            upcoming = None

        dumped_user = user_detail_schema.dump(user)
        dumped_invoices = invoices_schema.dump(invoices)
        response = {'data': {
            'user': dumped_user,
            'invoices': dumped_invoices,
            'upcoming_invoice': upcoming
        }}
        return response

    @route('/users/edit/<username>', methods=['PUT'])
    @admin_required
    def edit_user(self, username):
        """
        Admins can edit user accounts, for example if the username is
        offensive/goes against guidelines or update their permissions
        """
        # find the User
        user = User.find_by_identity(username)

        if user is None:
            response = {'error': USER_NOT_FOUND}
            return response, 404

        # load the json data
        json_data = request.get_json()

        # check for errors
        if not json_data:
            response = {'error': 'Invalid input.'}
            return response, 400

        try:
            data = admin_edit_user_schema.load(json_data)
        except ValidationError as err:
            response = {'error': err.messages}
            return response, 422

        # check if user is the last admin
        if User.is_last_admin(user, data['role']):
            response = {
                'error': 'User is the last admin in the system.'
            }
            return response, 400

        # is username being changed
        if user.username != data['username']:
            existing_username = User.find_by_identity(data['username'])
            if existing_username is None:
                user.username = data['username']
            else:
                response = {'error': 'Username is already taken.'}
                return response, 400

        user.role = data['role']
        user.save()

        headers = {'Location': url_for('AdminView:get_user',
                                       username=user.username)}
        return '', 204, headers

    @route('/users/bulk_delete', methods=['DELETE'])
    @admin_required
    def delete_users(self):
        """Option to bulk delete or delete a single user"""
        json_data = request.get_json()
        if not json_data:
            response = {'error': 'Invalid input.'}
            return response, 400

        try:
            data = bulk_delete_schema.load(json_data)
        except ValidationError as err:
            response = {'error': err.messages}
            return response, 422

        ids = User.get_bulk_action_ids(scope=data['scope'],
                                       ids=data['bulk_ids'],
                                       omit_ids=[current_user.id],
                                       query=request.args.get('q', text('')))

        # use a celery task to do this in the background
        from vidme.blueprints.admin.tasks import delete_users
        delete_users.delay(ids)

        response = {'data': {
            'deleted': True,
            'message': '{0} user(s) were scheduled to be deleted.'.format(
                len(ids))
        }}
        return response
