"""A simple web server to test HTTP client. Models itself after httpbin.
Portions of code have ben adapted from httpbin in the context of
`tornado.httpclient.AsyncHTTPClient`.

https://github.com/kennethreitz/httpbin

"""
from  tornado.escape import json_encode
from tornado.httputil import parse_body_arguments
from tornado.web import Application, RequestHandler, url

class HTTPBinRequestHandler(RequestHandler):

    def get_dict(self, *keys, **extras):
        """Returns request dict of given keys.

        This is taken from the httpbin source code and modified
        to fit `tornado.web.RequestHandler`.

        https://github.com/kennethreitz/httpbin/blob/master/httpbin/helpers.py#L113
        """

        request = self.request

        _keys = {
            'url',
            'args',
            'data',
            'origin',
            'headers',
            'files',
            'json'
        }

        assert _keys >= set(keys)

        args = {key: self.get_argument(key)
                        for key in request.arguments.keys()}

        body = request.body
        content_type = request.headers.get('Content-Type', '')

        data = {}
        files = {}


        if body:
            parse_body_arguments(content_type, body, data, files)

        def stringify(value):
            if isinstance(value, list):
                value = [stringify(item) for item in value]
            elif isinstance(value, bytes):
                value = value.decode('utf-8')
            elif isinstance(value, dict):
                value = {key: stringify(val) for key, val in value.items()}
            return value

        # Convert bytes to str
        data = stringify(data)

        def elmentify(value):
            if isinstance(value, list):
                if len(value) == 1:
                    value = value[0]
            return value

        data = {key:elmentify(value) for key, value in data.items()}

        try:
            _json = json_encode(data)
        except:
            _json = None

        xff = request.headers.get('X-Forwarded-For', '')
        origin = request.remote_ip
        if xff:
            origin = xff

        d = dict(
            url=request.uri,
            args=args,
            data=data,
            origin=origin,
            headers=request.headers,
            files=files,
            json=_json
        )

        out_d = dict()

        for key in keys:
            out_d[key] = d.get(key)

        out_d.update(extras)

        return out_d

class GetHandler(HTTPBinRequestHandler):
    """Handles simple GET requests"""

    def get(self):
        """Returns the passed in arguments as a JSON object. `url`, `args`,
        `headers` and the originating ip as `origin` are returned.
        """
        self.finish(self.get_dict('url', 'args', 'headers', 'origin'))

class PostHandler(HTTPBinRequestHandler):
    """Handles simple POST requests"""

    def post(self):
        """Returns the POST data as JSON. `url`, `args`, `data`, `files`,
        `json`, `headers` and the originating ip as `origin`
        are returned.
        """
        self.finish(self.get_dict(
            'url',
            'args',
            'data',
            'json',
            'files',
            'headers',
            'origin'
        ))

class PutHandler(HTTPBinRequestHandler):

    def put(self):
        """Returns the PUT data as JSON. `url`, `args`, `data`, `files`,
        `json`, `headers` and the originating ip as `origin`
        are returned.
        """
        self.finish(self.get_dict(
            'url',
            'args',
            'data',
            'json',
            'files',
            'headers',
            'origin'
        ))

class PatchHandler(HTTPBinRequestHandler):

    def patch(self):
        """Returns the PATCH data as JSON. `url`, `args`, `data`, `form`,
        `files`, `json`, `headers` and the originating ip as `origin`
        are returned.
        """
        self.finish(self.get_dict(
            'url',
            'args',
            'data',
            'json',
            'form',
            'files',
            'headers',
            'origin'
        ))

class DeleteHandler(HTTPBinRequestHandler):

    def delete(self):
        """Returns the DELETE data as JSON. `url`, `data`, `form`, `files`,
        `json`, `headers` and the originating ip as `origin` are returned.
        """
        self.finish(self.get_dict(
            'url',
            'args',
            'data',
            'json',
            'headers',
            'origin'
        ))

def httpbin():
    """Returns the tornado app to be used in sync with AsyncHTTPTestcase"""
    return Application([
        url('/get', GetHandler),
        url('/post', PostHandler),
        url('/patch', PatchHandler),
        url('/put', PutHandler),
    ])