import os
import subprocess
from tests.template_test import FlaskTestCase


class TestNodeData(FlaskTestCase):
    def test_basic_data(self):
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

        server_path = (os.path.join(os.path.dirname(os.getcwd()), "app-server.py"))
        #server_args = "-ip 127.0.0.1 -tm"
        client_process = subprocess.run(["python", server_path, "-ip 127.0.0.1", "-tm"], check=True)

        client_path = (os.path.join(os.path.dirname(os.getcwd()), "app-client.py"))
        client_args = f"-ip 127.0.0.1 -e -tm -t {node_token} -temp 20 -humidity 50 -bp 1000 -pm25 5 -pm10 10"
        client_p = subprocess.run(["python", client_path, client_args], check=True)
