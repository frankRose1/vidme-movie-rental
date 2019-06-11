from flask import jsonify, request

from vidme.api.v1 import V1FlaskView
from vidme.blueprints.admin.models import Dashboard
from lib.decorators import admin_required


class AdminView(V1FlaskView):

    @admin_required
    def get(self):
        """Count and group(by role) all users in the system"""
        group_and_count_users = Dashboard.group_and_count_users()
        response = jsonify(group_and_count_users)
        return response, 200
