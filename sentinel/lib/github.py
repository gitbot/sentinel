"""Github v3 API client for gitbot sentinel."""

__all__ = ['Github']

import binascii, json, os
from functools import wraps

from tornado.gen import coroutine

from . import requests

class ResponseError(requests.ResponseError):
    """Exception thrown for an unsuccessful Github API request.

    Attributes:

    * ``code`` - HTTP error integer error code.

    * ``response`` - `HTTPResponse` object.

    * ``error_body`` - The JSON body returned by Github.
    """
    def __init__(self, code, message=None, response=None):
        self.code = code
        self.error_message = message
        self.response = response
        desc = message
        if response:
            text = response.body.decode('utf-8')
            self.error_body = json.loads(text)
            if 'message' in self.error_body:
                desc = self.error_body['message']
        super().__init__(code, desc, response)

def gitroutine(meth):
    """
    A simple coroutine wrapper that translates meth:`requests.ResponseError`
    to a Github specific error object.
    """
    @wraps(meth)
    def wrapper(*args, **kwargs):
        """
        Wraps the function to translate the error.
        """
        try:
            response = yield meth(*args, **kwargs)
            text = response.body.decode('utf-8')
            return json.loads(text)
        except requests.ResponseError as error:
            raise ResponseError(error.code, error.message, error.response)
    return coroutine(wrapper)

class Github:
    """Provides a simple async interface to the github API v3."""

    def __init__(self, config=None):
        """
        :arg dict config configuration data for github communication.
            * oAuth Application credentials
            * URL's
        """
        self.config = config

    @coroutine
    def get_auth_url(self, scopes, callback_uri):
        """
        Get the oAuth authentication url for signing up / login
        with github credentials.

        :arg list scopes `Github API scopes`_ requested for access.
        "returns string The decorated github oAuth authentication url.
        """
        scope = ','.join(scopes) \
                        if isinstance(scopes, (list, tuple, set)) \
                        else '{}'.format(scopes)
        seed = binascii.hexlify(os.urandom(24))
        query = dict(
            client_id=self.config.github.auth.client_id,
            scope=scope,
            state=seed.decode('utf-8')
        )
        return (self.config.github.urls.auth + \
            requests.Params(query).to_query_string(question_prefix=True))

    @gitroutine
    def get_acess_token(self, code, state):
        """
        Get the oAuth token from the given access code.

        :arg string code The github oAuth code from the auth url request.
        :arg string state The state parameter from the previous request.
        :returns string The github oAuth token.
        """
        data = dict(
            client_id=self.config.github.client_id,
            client_secret=self.config.github.client_secret,
            code=code,
            state=state
        )
        return requests.post(
            self.config.github.urls.token,
            headers=dict(Accept='application/json'),
            data=data
        )

    @gitroutine
    def get_user_profile(self, token):
        """
        Get the user profile for the given oAuth token.

        :arg string token The github oAuth token.
        :returns dict The github user profile associated with this token.
        """
        query = dict(access_token=token)
        return requests.get(
            self.config.github.urls.profile,
            headers=dict(Accept='application/json'),
            params=query
        )
