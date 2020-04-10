from AQM import app
from flask import url_for
import unittest
import os
import dbm


class FlaskTestCase(unittest.TestCase):
    def setUp(self):
        # Change to AQM directory
        os.chdir(os.path.join(os.path.dirname(os.getcwd()), "AQM"))

        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['DATABASE'] = 'test_database.sqlite3'
        self.app = app.test_client()

    def tearDown(self):
        dbm.drop_all()

    def register(self, username, email, password, confirm_password):
        return self.app.post('/register', data=dict(username=username, email=email, password=password,
                                                    confirm_password=confirm_password,
                                                    submit="Sign Up"), follow_redirects=True)

    def test_index_status_code(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_register(self):
        response = self.app.get('/register', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        response = self.app.post('/register', data={'username': 'test', 'email': 'test@test.com', 'password': 'test',
                                                    'confirm_password': 'test', 'submit': 'Sign Up'},
                                 follow_redirects=True)
        assert b'Welcome test, your account has been registered successfully!' in response.data

    def test_positive_login(self):
        response = self.register('test', 'test@test.com', 'test', 'test')
        self.assertEqual(response.status_code, 200)

        response = self.app.get('/login', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        response = self.app.post('/login', data={'username': 'test', 'password': 'test', 'submit': 'Login'},
                                 follow_redirects=True)
        self.assertIn(b'Account', response.data)

    # def test_false_login(self):
    #     pass


if __name__ == '__main__':
    unittest.main()
