import unittest

from commando.conf import ConfigDict
from fswrap import File
from tornado.testing import gen_test, AsyncTestCase
import yaml

from sentinel.lib.github import Github


HERE = File(__file__).parent
TEST_ROOT = HERE.parent
TEST_CONF = TEST_ROOT.child_file('~test_conf.yaml')
CONF = None

if TEST_CONF.exists:
    """
    #../../~test_conf.yaml
    github:
      auth:
        client_id: <Github Application client id>
        client_secret: <Github Application client secret>
      urls:
        auth: https://github.com/login/oauth/authorize
        token: https://github.com/login/oauth/access_token
        profile: https://api.github.com/user
    test_data:
      profile:
        token: <oAuth token for testing github profile API>
        data:
          id: <profile id for the above token>
          login: <login for the above token>
          email: <email for the above token>
          html_url: https://github.com/<login for the above token>
    """
    CONF = ConfigDict(yaml.load(TEST_CONF.read_all()))

class GithubTest(AsyncTestCase):

    @gen_test
    @unittest.skipUnless(TEST_CONF.exists, 'Configuration file not found.')
    def test_github_auth_url(self):

        github = Github(CONF)
        result = yield github.get_auth_url(['repo'], 'http://localhost:8080')
        assert 'https://github.com/login/oauth/authorize' in result
        assert 'scope=repo' in result
        assert 'state=' in result
        assert 'client_id=' in result


    @gen_test
    @unittest.skipUnless(TEST_CONF.exists, 'Configuration file not found.')
    def test_github_profile(self):

        github = Github(CONF)
        result = yield github.get_user_profile(CONF.test_data.profile.token)
        assert result
        for key, value in CONF.test_data.profile.data.items():
            assert key in result
            assert result[key] == value
