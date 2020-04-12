from AQM import app
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

    """
    Helper functions 
    """
    def register(self, username, email, password, confirm_password):
        return self.app.post('/register', data=dict(username=username, email=email, password=password,
                                                    confirm_password=confirm_password,
                                                    submit="Sign Up"), follow_redirects=True)

