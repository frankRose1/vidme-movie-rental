from flask_classful import FlaskView


class V1FlaskView(FlaskView):
    """
    Inherits from flask_classful.FlaskView
    Prefix any version 1 enpoints with "/api/v1"
    """
    route_prefix = '/api/v1'