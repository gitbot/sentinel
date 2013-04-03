"""Async HTTP Requests for humans."""
from functools import wraps
from tornado.escape import json_encode
from urllib.parse import quote_plus, urlencode

from tornado.gen import coroutine
from tornado.httpclient import AsyncHTTPClient, HTTPError


def make_query_string(params, safe=None):
    """
    Make query string from a given dictionary or a mapping iterable.

    :arg dict params: The key, value pairs of a query string.
    :arg string safe: The `safe` characters that can be allowed when escaping.
        See :py:func: `urllib.parse.quote_plus` for more information.

    :returns string Quoted query string.
    """

    def param(key, value):
        """key + quoted value"""
        return key + '=' + quote_plus(value, safe=safe or '')

    return '&'.join((param(key, value) for key, value in params.items()))


class Params(dict):
    """Request parameters. Provides transformations to JSON & querystring."""

    def __repr__(self):
        """Default representation.
        :returns string query string representation of params.
        """
        return self.to_query_string()

    def to_json(self):
        """Transforms parameters to their JSON representation.

        :returns string JSON representation of params.

        """
        return json_encode(self)

    def to_query_string(self, question_prefix=False):
        """Querystring representation.

        :arg boolean question_prefix If True and the dictionary is not empty,
        the returned query string is prefixed with a question mark.

        :returns string query string representation of params.
        """
        qs = make_query_string(self)
        return '?' + qs if question_prefix and len(qs) > 0 else qs

def httproutine(meth):
    """
    A simple coroutine wrapper that translates `tornado.httpclient.HTTPError`
    to a `requests.ResponseError` object.
    """
    @wraps(meth)
    def wrapper(*args, **kwargs):
        """
        Wraps the function to translate the error.
        """
        try:
            return (yield meth(*args, **kwargs))
        except HTTPError as error:
            raise ResponseError(error.code, error.args[0], error.response)
    return coroutine(wrapper)

class ResponseError(Exception):
    """Exception thrown for an unsuccessful HTTP request.

    Attributes:

    * ``code`` - HTTP error integer error code, e.g. 404.  Error code 599 is
      used when no HTTP response was received, e.g. for a timeout.

    * ``response`` - `HTTPResponse` object, if any.

    Note that if ``follow_redirects`` is False, redirects become HTTPErrors,
    and you can look at ``error.response.headers['Location']`` to see the
    destination of the redirect.
    """
    def __init__(self, code, message=None, response=None):
        self.code = code
        self.error_message = message
        self.response = response
        super().__init__(self.error_message)

@httproutine
def get(base_url, headers=None, params=None, io_loop=None):
    """Make an async get request to the given url using the given headers
        and params.

    :arg string base_url The url to request.
    :arg dict headers The HTTP headers for the request.
    :arg dict params The parameters to pass as a query string.
    :arg dict io_loop The io_loop to use for the async request.
    """

    # TODO: Add authentication parameters
    qs = Params(params or dict()).to_query_string(question_prefix=True)
    url = base_url + qs
    return AsyncHTTPClient(io_loop=io_loop).fetch(url, headers=headers)

@httproutine
def post(url, headers=None, data=None, io_loop=None):
    """Make an async post request to the given url using the given headers
        and data.

    :arg string url The url to request.
    :arg dict headers The HTTP headers for the request.
    :arg dict data The parameters to pass as the request body.
    :arg dict io_loop The io_loop to use for the async request.
    """

    # TODO: Add authentication parameters
    return AsyncHTTPClient(io_loop=io_loop).fetch(
        url,
        method='POST',
        body=urlencode(data),
        headers=headers)