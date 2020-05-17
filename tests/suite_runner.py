import unittest
from tests import test_status_codes
from tests import test_user_register
from tests import test_login
from tests import test_node_register
from tests import test_node_data
from tests import test_removal


if __name__ == '__main__':
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromModule(test_status_codes))
    suite.addTests(loader.loadTestsFromModule(test_user_register))
    suite.addTests(loader.loadTestsFromModule(test_login))
    suite.addTests(loader.loadTestsFromModule(test_node_register))
    suite.addTests(loader.loadTestsFromModule(test_node_data))
    suite.addTests(loader.loadTestsFromModule(test_removal))

    runner = unittest.TextTestRunner(verbosity=3)
    result = runner.run(suite)
