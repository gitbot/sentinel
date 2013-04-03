"""Gitbot oAuth handler application

Handles oAuth bridging between sentinel and the github API.
"""

from tornado.gen import coroutine
from tornado.web import asynchronous, RequestHandler, url


class AuthURLHandler(RequestHandler):
    pass


class GetTokenHandler(RequestHandler):
    pass


class GetProfileHandler(RequestHandler):
    pass


class LogoutHandler(RequestHandler):
    pass


def mount(application, mount_point='/'):


