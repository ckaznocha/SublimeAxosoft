"""
Tests.

Tests for the axosoftAPI
"""
import unittest
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from xvfbwrapper import Xvfb
try:
    from urllib.parse import urlparse, parse_qs
except ImportError:
    from urlparse import urlparse, parse_qs
from axosoft_api import Axosoft

if os.environ.get('TRAVIS', False) is False:
    import axosoft_credentials

client_id = os.environ.get('CLIENT_ID')
client_secret = os.environ.get('CLIENT_SECRET')
axosoft_user = os.environ.get('AXOSOFT_USER')
axosoft_password = os.environ.get('AXOSOFT_PASSWORD')


class TestClientCreation(unittest.TestCase):
    def setUp(self):
        self.client_id = client_id
        self.client_secret = client_secret

    def test_creation(self):
        self.axosoft_client = Axosoft(
            self.client_id, self.client_secret,
            'sublime-axosoft.axosoft.com'
        )
        self.assertIsInstance(self.axosoft_client, Axosoft)


class TestChangeAPIVersion(unittest.TestCase):
    def setUp(self):
        self.client_id = client_id
        self.client_secret = client_secret
        self.axosoft_client = Axosoft(
            self.client_id, self.client_secret,
            'sublime-axosoft.axosoft.com'
        )

    def test_valid_api_version(self):
        try:
            self.axosoft_client.set_api_version(3)
        except LookupError:
            self.fail("set_api_version() raised LookupError unexpectedly!")

    def test_invalid_api_version(self):
        self.assertRaises(
            LookupError,
            self.axosoft_client.set_api_version,
            2
        )

class TestClientAuthenticationPassword(unittest.TestCase):
    def setUp(self):
        self.client_id = client_id
        self.client_secret = client_secret
        self.axosoft_client = Axosoft(
            self.client_id, self.client_secret,
            'sublime-axosoft.axosoft.com'
        )

    def test_password_auth(self):
        token = self.axosoft_client.authenticate_by_password(
            axosoft_user,
            axosoft_password
        )
        self.assertIsNotNone(token)
        is_authenticated = self.axosoft_client.is_authenticated()
        self.assertTrue(is_authenticated)

        second_token = self.axosoft_client.authenticate_by_password(
            axosoft_user,
            axosoft_password
        )
        self.assertIsNotNone(second_token)
        self.assertTrue(is_authenticated)

        r = self.axosoft_client.get('me')
        self.assertEquals(axosoft_user, r['data']['email'])

        logged_out = self.axosoft_client.log_out()
        self.assertTrue(logged_out)

    def test_unauthenticated(self):
        is_authenticated = self.axosoft_client.is_authenticated()
        self.assertFalse(is_authenticated)

    def test_bad_auth_token(self):
        axosoft_client = Axosoft(
            self.client_id,
            self.client_secret,
            'sublime-axosoft.axosoft.com',
            '3et4ae1a-7025-45gt-84a3-a1391ts9a376'
        )
        is_authenticated = axosoft_client.is_authenticated()
        self.assertFalse(is_authenticated)

    def test_bad_auth_secret(self):
        axosoft_client = Axosoft(
            self.client_id,
            'foo',
            'sublime-axosoft.axosoft.com',
            '3et4ae1a-7025-45gt-84a3-a1391ts9a376'
        )
        self.assertRaises(
            ValueError,
            axosoft_client.authenticate_by_password,
            axosoft_user,
            axosoft_password
        )

class TestClientAuthenticationCode(unittest.TestCase):
    def setUp(self):
        self.client_id = client_id
        self.client_secret = client_secret
        self.axosoft_client = Axosoft(
            self.client_id, self.client_secret,
            'sublime-axosoft.axosoft.com'
        )
        self.xvfb = Xvfb(width=1280, height=720)
        self.xvfb.start()
        self.driver = webdriver.Firefox()

    def test_code_auth(self):
        redirect_uri = "http://foo.bar/"
        url = self.axosoft_client.begin_authentication_by_code(
            redirect_uri
        )
        res_url = urlparse(url)
        self.assertEquals("sublime-axosoft.axosoft.com", res_url.netloc)
        self.assertEquals("https", res_url.scheme)
        query_string = parse_qs(res_url.query)
        self.assertEquals(["read write"], query_string["scope"])
        self.assertEquals([redirect_uri], query_string["redirect_uri"])
        self.assertEquals(["code"], query_string["response_type"])
        self.assertEquals([self.client_id], query_string["client_id"])

        driver = self.driver
        driver.get(url)
        self.assertEquals("Axosoft", driver.title)
        driver.find_element_by_name("ctl00$BodyContent$userNameTextbox")\
            .send_keys(axosoft_user)
        elem = driver.find_element_by_name("ctl00$BodyContent$passwordTextbox")
        elem.send_keys(axosoft_password)
        elem.send_keys(Keys.RETURN)
        driver.implicitly_wait(10)
        driver.find_element_by_class_name("saveAndClose").click()
        end_url = urlparse(driver.current_url)
        self.assertEquals("foo.bar", end_url.netloc)
        query_string = parse_qs(end_url.query)
        code = query_string["code"]

        token = self.axosoft_client.complete_authentication_by_code(
            code,
            redirect_uri
        )

        self.assertIsNotNone(token)
        is_authenticated = self.axosoft_client.is_authenticated()
        self.assertTrue(is_authenticated)

        second_token = self.axosoft_client.complete_authentication_by_code(
            code,
            redirect_uri
        )
        self.assertIsNotNone(second_token)
        is_authenticated = self.axosoft_client.is_authenticated()
        self.assertTrue(is_authenticated)

        logged_out = self.axosoft_client.log_out()
        self.assertTrue(logged_out)
        is_authenticated = self.axosoft_client.is_authenticated()
        self.assertFalse(is_authenticated)

    def tearDown(self):
        self.driver.close()
        self.xvfb.stop


class TestClientMethods(unittest.TestCase):
    def setUp(self):
        self.client_id = client_id
        self.client_secret = client_secret
        self.axosoft_client = Axosoft(
            self.client_id, self.client_secret,
            'sublime-axosoft.axosoft.com'
        )
        self.axosoft_client.authenticate_by_password(
            axosoft_user,
            axosoft_password
        )

    def test_invalid_endpoint(self):
        self.assertRaises(LookupError, self.axosoft_client.get, 'foo')
        self.assertRaises(LookupError, self.axosoft_client.update, 'me', '3', {})
        self.assertRaises(LookupError, self.axosoft_client.get, 'features', '3', {}, 'foo')
        self.assertRaises(LookupError, self.axosoft_client.get, 'me', element='foo')


    def test_get_resourse(self):
        r = self.axosoft_client.get('me')
        self.assertEquals(axosoft_user, r['data']['email'])
        r = self.axosoft_client.get('features', '5', element='emails')
        self.assertEquals('test', r['data'][0]['body'])


    def test_resourse_create(self):
        r = self.axosoft_client.create('releases', payload={'name': 'testRelease', 'release_type': {'id': 1}})
        self.assertEquals(int, type(r['data']['id']))
        self.assertRaises(ValueError, self.axosoft_client.create, 'releases', {})
        r = self.axosoft_client.create('releases', payload={'name': 'testRelease', 'release_type': {'id': 1}})
        self.assertEquals(int, type(r['data']['id']))
        r = self.axosoft_client.create('features', {'user_ids': [1]}, '5', 'notifications')
        self.assertEquals(int, type(r['data']['id']))

    def test_resourse_update(self):
        r = self.axosoft_client.create('releases', payload={'name': 'testRelease', 'release_type': {'id': 1}})
        r = self.axosoft_client.get('releases', r['data']['id'])
        self.assertEquals(r['data']['name'], 'testRelease')
        r = self.axosoft_client.update('releases', r['data']['id'], payload={'name': 'testRelease', 'release_type': {'id': 1}})
        self.assertEquals(int, type(r['data']['id']))
        self.assertRaises(ValueError, self.axosoft_client.update, 'releases', '', {})

    def test_resourse_delete(self):
        r = self.axosoft_client.create('releases', payload={'name': 'testRelease', 'release_type': {'id': 1}})
        r = self.axosoft_client.delete('releases', r['data']['id'])
        self.assertTrue(r)
