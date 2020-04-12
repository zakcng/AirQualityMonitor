from tests.template_test import FlaskTestCase


class TestRegister(FlaskTestCase):
    # Register Tests
    def test_positive_register(self):
        response = self.app.get('/register', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        response = self.app.post('/register', data={'username': 'test', 'email': 'test@test.com', 'password': 'test',
                                                    'confirm_password': 'test', 'submit': 'Sign Up'},
                                 follow_redirects=True)
        assert b'Welcome test, your account has been registered successfully!' in response.data