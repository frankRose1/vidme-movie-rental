from flask import jsonify, request
from flask_classful import route
from sqlalchemy import text

# from lib.decorators import admin_required
from vidme.api.v1 import V1FlaskView
from vidme.blueprints.admin.models import Dashboard
from vidme.blueprints.admin.schemas import admin_edit_user_schema, user_schema
from vidme.blueprints.user.models import User


USER_NOT_FOUND = 'User not found.'

class AdminView(V1FlaskView):

    # @admin_required
    def index(self):
        """
        Count and group(by role) all users in the system. Will show a
        summary of total users in the DB as well as what percentage are members
        and admins.
        """
        group_and_count_users = Dashboard.group_and_count_users()
        response = jsonify(group_and_count_users)
        return response, 200

    @route('/users/', methods=['GET'])
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
            .filter(User.search(request.args.get('q', ''))) \
            .order_by(user.role.asc(), text(order_values)) \
            .paginate(page, page_size, True)
        
        response = { 'users': paginated_users }
        return jsonify(response), 200

    @route('/users/edit/<int:id>/', methods=['PUT'])
    def edit_user(self, id):
        """Admins can edit user accounts, for example if the username is 
        offensive/goes against guidelines or update their permissions
        """
        # find the User
        user = User.query.filter(id=id).first()

        if user is None:
            response = jsonify({'error': USER_NOT_FOUND})
            return response, 404
        
        # load the json data
        json_data = request.get_json()

        # check for errors
        if not json_data:
            response = jsonify({ 'error': 'Invalid input.' })
            return response, 400
        
        data, errors = admin_edit_user_schema(json_data)

        if errors:
            response = jsonify({'error': errors})
            return response, 422

        # check if user is the last admin
        if User.is_last_admin(user, data['role']):
            response = {
                'error': 'User is the last admin in the system.'
            }
            return jsonify(response), 400
        
        # is username being changed
        if user.username != data['username']:
            existing_username = User.find_by_identity(data['username'])
            if existing_username is None:
                user.username = data['username']
            else:
                response = jsonify({'error': 'Username is already taken.'})
                return response, 400

        user.role = data['role']
        user.save()

        return jsonify(data), 200

    @route('/users/<int:id>/', methods=['GET'])
    def get_user(self, id):
        """Allows an admin to fetch specific user data
        """
        user = User.query.filter(id=id).first()

        if User is None:
            response = {
                'error': USER_NOT_FOUND
            }
            return jsonify(response), 404

        result = user_schema.dump(user)

        return result.data, 200

    @route('/users/delete/<int:id>/', methods=['DELETE'])
    def delete_user(self, id):
        """Admins can delete user accounts
        """
        user = User.query.filter(id=id).first()

        if User is None:
            response = {
                'error': USER_NOT_FOUND
            }
            return jsonify(response), 404
        
        user.delete()
        response = {
            'message': 'User was deleted successfully',
            'deleted_id': user.id
        }

        return jsonify(response), 200
