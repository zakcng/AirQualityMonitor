from tests.template_test import FlaskTestCase


def create_node(self, node_name, node_location):
    response = self.create_node(node_name, node_location)
    self.assertEqual(response.status_code, 200)

    return response


class TestNodeRegister(FlaskTestCase):
    def test_create_node(self):
        self.register_admin()
        self.login('admin', 'admin')

        response = self.app.get('/admin-cp', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        node_name = 'Test Node'
        node_location = 'Test Location'
        response = create_node(self, node_name, node_location)
        assert f'Node {node_name} created'.encode() in response.data

    def test_create_duplicate_node(self):
        self.register_admin()
        self.login('admin', 'admin')

        response = self.app.get('/admin-cp', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        node_name = 'Test Node'
        node_location = 'Test Location'
        response = create_node(self, node_name, node_location)
        assert f'Node {node_name} created'.encode() in response.data

        node_name = 'Test Node'
        node_location = 'Test Location'
        response = create_node(self, node_name, node_location)
        assert f'Node creation unsuccessful - Duplicate node name provided'.encode() in response.data
