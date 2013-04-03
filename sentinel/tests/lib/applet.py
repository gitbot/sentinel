"""
A simple module to facilitate composable asynchronous applications.
"""
import tornado.web.Application

class Applet(object):
    """
    A simple collection of request handlers
    """
    def __init__(self, handlers, host_pattern='.*$'):
        """
        Accepts an immutable list of handlers.
        :arg list handlers A list of request handlers.
        :arg string host_pattern Host pattern of the handlers.
        """
        self.handlers = handlers
        self.host_pattern = host_pattern

    def __call__(self, application=None):
        """
        This is used to mount the handlers in the
        applet onto a new `tornado.web.Application` object or
        an existing one thats passed in.

        :arg tornado.web.Application application The application providing the
        mount point for the handlers in the applet. A new application object is
        created if this argument is `None`.
        """
        if not application:
            application = Application()

        application.add_handlers(self.host_pattern, self.handlers)
        return application



class Application(tornado.web.Application):

