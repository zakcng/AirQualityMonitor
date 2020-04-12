import unittest
from tests import test_status_codes


if __name__ == '__main__':
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromModule(test_status_codes))

    runner = unittest.TextTestRunner(verbosity=3)
    result = runner.run(suite)
