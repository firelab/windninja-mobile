"""
This script runs the windninjaweb application using a development server.
"""
import unittest

import tests.tests_config
import tests.tests_utility

if __name__ == "__main__":
    # unittest.main(module="tests")

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(tests.tests_config.TestConfig))
    suite.addTests(loader.loadTestsFromTestCase(tests.tests_utility.TestUtility))
    unittest.TextTestRunner().run(suite)
