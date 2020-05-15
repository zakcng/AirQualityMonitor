import os
import subprocess
import time
from tests.template_test import FlaskTestCase


class TestNodeData(FlaskTestCase):
    def test_user_removal(self):
        response = self.app.post('/register', data={'username': 'test', 'email': 'test@test.com', 'password': 'test',
                                                    'confirm_password': 'test', 'submit': 'Sign Up'},
                                 follow_redirects=True)

        assert b'Welcome test, your account has been registered successfully!' in response.data

        self.register_admin()
        self.login('admin', 'admin')

        response = self.app.post('/admin-cp',
                                 data={'account_name': 'test', 'remove_user': 'true'},
                                 follow_redirects=True)
        print(response.data)
        assert f'Removed user test successfully'.encode() in response.data

    def test_node_removal(self):
        # TODO: Ensure node data is also removed.
        self.register_admin()
        self.login('admin', 'admin')

        response = self.app.get('/admin-cp', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        node_name = 'Test Node'
        node_location = 'Test Location'
        response = self.create_node(node_name, node_location)
        self.assertEqual(response.status_code, 200)

        # Calculate node_id
        node_id = self.get_node_id(node_name)
        node_token = self.get_node_token(node_name)

        # Run processes
        server_path = (os.path.join(os.path.dirname(os.getcwd()), "app-server.py"))
        server_process = subprocess.Popen(["python", server_path, "-ip", "127.0.0.1", "-tm"])

        time.sleep(5)

        client_path = (os.path.join(os.path.dirname(os.getcwd()), "app-client.py"))
        client_process = subprocess.Popen(
            ["python", client_path, "-ip", "127.0.0.1", "-e", "-tm", "-t", node_token, "-temp", "69", "-humidity", "50",
             "-bp", "1000", "-pm25", "5", "-pm10", "10"])

        time.sleep(5)

        # Terminate processes
        server_process.kill()
        client_process.kill()

        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<td>69.0</td>', response.data)
