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
        response = self.app.get('/register', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    # Admin view
    def test_admin_control_panel_status_code_positive(self):
        """
        Test status code of admin control panel.
        """
        self.register_admin()

        response = self.login("admin", "admin")
        self.assertEqual(response.status_code, 200)

        response = self.app.get('/admin-cp', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_admin_control_panel_status_code_negative_non_admin(self):
        """
        Test status code of admin control panel with non-admin login ensure it fails on the redirect to index page.
        """
        response = self.register('test', 'test@test.com', 'test', 'test')
        self.assertEqual(response.status_code, 200)

        response = self.login("test", "test")
        self.assertEqual(response.status_code, 200)

        # Check it fails redirect to index (/)
        response = self.app.get('/admin-cp', follow_redirects=False)
        self.assertEqual(response.status_code, 302)

    def test_admin_control_panel_status_code_negative_no_login(self):
        """
        Test status code of admin control panel without logging in.
        Expected result: 401 Unauthorized
        """
        response = self.app.get('/admin-cp', follow_redirects=True)
        self.assertEqual(response.status_code, 401)

    # User view
    def test_account_management_status_code_negative_no_login(self):
        """
        Test status code of account page without logging in.
        Expected result: 401 Unauthorized
        """
        response = self.app.get('/account', follow_redirects=True)
        self.assertEqual(response.status_code, 401)

    def test_account_management_status_code_positive(self):
        response = self.register('test', 'test@test.com', 'test', 'test')
        self.assertEqual(response.status_code, 200)

        response = self.login("test", "test")
        self.assertEqual(response.status_code, 200)

        # Check it fails redirect to index (/)
        response = self.app.get('/account', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
