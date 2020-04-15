from tests.template_test import FlaskTestCase
from tests.test_node_register import TestNodeRegister


class TestNodeData(FlaskTestCase):
    def test_basic_data(self):
        node_id = TestNodeRegister.test_create_node(self)
        print(node_id)
