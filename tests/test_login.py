from tests.template_test import FlaskTestCase


class TestLogin(FlaskTestCase):
    # Login Tests
    def test_positive_login(self):
        response = self.register('test', 'test@test.com', 'test', 'test')
        self.assertEqual(response.status_code, 200)

        response = self.app.get('/login', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        response = self.app.post('/login', data={'username': 'test', 'password': 'test', 'submit': 'Login'},
                                 follow_redirects=True)
        self.assertIn(b'Account', response.data)

    def test_false_login(self):
        response = self.app.get('/login', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        response = self.app.post('/login', data={'username': 'test', 'password': 'test', 'submit': 'Login'},
                                 follow_redirects=True)
        self.assertIn(b'Login attempt unsuccessful. Please check credentials and try again!', response.data)