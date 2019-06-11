from flask import jsonify, request
from flask_classful import route

from vidme.api.v1 import V1FlaskView
from vidme.blueprints.admin.models import Dashboard
from lib.decorators import admin_required


class AdminView(V1FlaskView):

    @route('/users/', methods=['GET'])
    @admin_required
    def users(self):
        """Count and group(by role) all users in the system"""
        group_and_count_users = Dashboard.group_and_count_users()
        response = jsonify(group_and_count_users)
        return response, 200
