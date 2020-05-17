from tests.template_test import FlaskTestCase


class TestLogin(FlaskTestCase):
    # Login Tests
    def test_positive_user_login(self):
        response = self.register('test', 'test@test.com', 'test', 'test')
        self.assertEqual(response.status_code, 200)

        response = self.app.get('/login', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.login("test", "test")
        self.assertIn(b'Account', response.data)

    def test_negative_user_login(self):
        response = self.register('test', 'test@test.com', 'test', 'test')
        self.assertEqual(response.status_code, 200)

        response = self.app.get('/login', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        response = self.login("test", "test1")
        self.assertIn(b'Login attempt unsuccessful. Please check credentials and try again!', response.data)