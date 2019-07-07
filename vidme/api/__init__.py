from lib.representations import output_json


class JSONViewMixin(object):
    """
    Add lib.output_json to representations so that FlaskViews can respond
    with additional headers.
    """
    representations = {
        'application/json': output_json,
        'flask-classful/default': output_json,
    }
