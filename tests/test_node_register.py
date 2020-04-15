from tests.template_test import FlaskTestCase


def create_node(self, node_name, node_location):
    response = self.create_node(node_name, node_location)
    self.assertEqual(response.status_code, 200)
    assert f'Node {node_name} created'.encode() in response.data

    # Calculate node_id
    node_id = self.get_node_id(node_name)
    return node_id


class TestNodeRegister(FlaskTestCase):
    def test_create_node(self):
        self.register_admin()
        self.login('admin', 'admin')

        response = self.app.get('/admin-cp', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        create_node(self, 'Test Node', 'Test Location')

    # def test_create_duplicate_node(self):
    #     self.register_admin()
    #     self.login('admin', 'admin')
    #
    #     response = self.app.get('/admin-cp', follow_redirects=True)
    #     self.assertEqual(response.status_code, 200)
    #
    #     create_node(self, 'Test Node', 'Test Location')
    #     create_node(self, 'Test Node', 'Test Location')
