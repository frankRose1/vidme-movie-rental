import json

from flask import make_response


def output_json(data, code=200, headers=None):
    """
    Returns a JSON response in our API views, including headers, and a status
    code.

    :param data: Dict of data
    :param code: Status code, defaults to 200
    :headers: Any headers to send to the client
    :return: Result from flask.make_response() 
    """
    content_type = 'application/json'
    dumped = json.dumps(data)
    if headers:
        headers.update({'Content-Type': content_type})
    else:
        headers = {'Content-Type': content_type}
    
    response = make_response(dumped, code, headers)
    return response
