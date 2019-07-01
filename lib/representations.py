import json

from flask import make_response


def output_json(data, code=200, headers=None):
    """
    Returns a JSON response in our API views, including headers, and a status
    code.

    :param data: Data to send to the client
    :type data: dict
    :param code: Status code of the response, defaults to 200
    :type code: int
    :param headers: Any headers to send to the client
    :type headers: dict
    :return: Result from flask.make_response()
    """
    content_type = 'application/json'
    # for a 204 status code
    if data == '':
        dumped = data
    else:
        dumped = json.dumps(data)

    if headers:
        headers.update({'Content-Type': content_type})
    else:
        headers = {'Content-Type': content_type}
    
    response = make_response(dumped, code, headers)
    return response
