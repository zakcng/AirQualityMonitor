from AQM import app
import unittest
import os


class FlaskTestCase(unittest.TestCase):
    def setUp(self):
        os.chdir(os.path.join(os.getcwd(), "AQM"))
        # Database configuration
        import dbm
        dbm.db_path = "test_database.sqlite3"
        dbm.db_exists()

        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['DATABASE'] = 'test_database.sqlite3'
        self.app = app.test_client()

    def tearDown(self):
        pass

    def test_index_status_code(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()