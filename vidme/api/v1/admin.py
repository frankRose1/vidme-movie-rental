from flask import jsonify, request
from flask_jwt_exteneded import jwt_required

from vidme.api.v1 import V1FlaskView
from vidme.blueprints.admin.models import Dashboard


# TODO need to set up a custom decorator to protect from non-admins
class AdminView(V1FlaskView):

    @jwt_required
    def get(self):
        """Count and group(by role) all users in the system"""
        group_and_count_users = Dashboard.group_and_count_users()
        response = jsonify(group_and_count_users)
        return response, 200
