import json

from tornado.testing import gen_test, AsyncHTTPTestCase

from sentinel.lib import requests
from sentinel.lib.requests import make_query_string

from sentinel.tests.util import httpbin


class RequestsTest(AsyncHTTPTestCase):


    def get_app(self):
        return httpbin()

    def test_app(self):
        headers = {
            "Content-type": "application/json",
            "Accept": "text/plain"
        }
        params = {
            "a": "1",
            "b": "3"
        }
        url = '/get?{}'.format(make_query_string(params))
        response = self.fetch(url, headers=headers)
        assert response
        assert response.body
        text = response.body.decode('utf-8')
        args = json.loads(text)['args']
        assert args['a'] == params['a']
        assert args['b'] == params['b']

    @gen_test
    def test_requests_get(self):
        headers = {
            "Content-type": "application/json",
            "Accept": "text/plain"
        }
        params = {
            "a": "1",
            "b": "3"
        }
        url = '{}://localhost:{}/get'.format(
            self.get_protocol(),
            self.get_http_port()
        )
        response = yield requests.get(url, headers=headers, params=params)
        assert response
        assert response.body
        text = response.body.decode('utf-8')
        args = json.loads(text)['args']
        assert args['a'] == params['a']
        assert args['b'] == params['b']

    @gen_test
    def test_requests_post(self):
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
            "Accept": "text/plain"
        }
        params = {
            "a": "1",
            "b": "3"
        }
        url = '{}://localhost:{}/post'.format(
            self.get_protocol(),
            self.get_http_port()
        )
        response = yield requests.post(url,
            headers=headers,
            data=params)
        assert response
        assert response.body
        text = response.body.decode('utf-8')
        args = json.loads(text)['data']
        assert args['a'] == params['a']
        assert args['b'] == params['b']
