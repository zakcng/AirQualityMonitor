from tests.template_test import FlaskTestCase


class TestStatusCodes(FlaskTestCase):
    # Page Status Codes Tests
    def test_index_status_code(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_nodes_status_code(self):
        response = self.app.get('/nodes', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_about_status_code(self):
        response = self.app.get('/about', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_login_status_code(self):
        response = self.app.get('/login', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_login_register_status_code(self):
        response = self.app.get('/login', follow_redirects=True)
        self.assertEqual(response.status_code, 200)