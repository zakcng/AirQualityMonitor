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

        # Initialise
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Drop all
        dbm.drop_all()

    def tearDown(self):
        # Drop all
        dbm.drop_all()

    """
    Helper functions 
    """

    def register(self, username, email, password, confirm_password):
        # Register an account via post data to register page
        return self.app.post('/register', data=dict(username=username, email=email, password=password,
                                                    confirm_password=confirm_password,
                                                    submit="Sign Up"), follow_redirects=True)

    def login(self, username, password):
        # Login a user via post data to login page
        return self.app.post('/login', data={'username': username, 'password': password, 'submit': 'Login'},
                             follow_redirects=True)

    def create_node(self, node_name, node_location):
        return self.app.post('/admin-cp',
                             data={'nodeName': node_name, 'nodeLocation': node_location, 'nodeAdd': 'Add Node'},
                             follow_redirects=True)

    def get_node_id(self, node_name):
        # Function to return the node_id in relation to the nodes name.
        return dbm.get_node_id_by_name(node_name)

    def get_node_token(self, node_name):
        return dbm.get_node_token_by_name(node_name)

    # Static functions
    @staticmethod
    def register_admin(username='admin', email='admin@admin.com',
                       password='$2b$12$yZNLO93MQ9E1bkCdkowVLe3C/0SieARNigJFZ/0d85buWJ.M5om6m'):
        # Function to create an admin account via database insertion
        dbm.insert_user(username=username, password=password, email=email, user_type=0)
