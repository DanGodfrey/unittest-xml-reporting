# -*- coding: utf-8 -*-

"""Custom Django test runner that runs the tests using the
XMLTestRunner class.

The main reason that made me come up with this project in the first place was
to make it easier to manage the build cycle of my Django applications. Since
I already use Hudson to build my JavaEE applications, it would be nice to
leverage my current setup to handle my Django applications as well.

This script shows how to use the XMLTestRunner in a Django project. To know
how to configure a custom TestRunner in a Django project, please read the
Django docs website.

To fine tune this script, put one or more of the following settings in your
project's 'settings.py' file:

 - TEST_OUTPUT_VERBOSE (default: False)
    Besides the XML reports generated by the test runner, a bunch of useful
    information is printed to the sys.stderr stream, just like the
    TextTestRunner does. Use this setting to choose between a verbose and a
    non-verbose output.

 - TEST_OUTPUT_DESCRIPTIONS (default: False)
    If your test methods contains docstrings, you can display such docstrings
    instead of display the test name (ex: module.TestCase.test_method). In
    order to use this feature, you have to enable verbose output by setting
    TEST_OUTPUT_VERBOSE = True.

 - TEST_OUTPUT_DIR (default:'.')
    Tells the test runner where to put the XML reports. If the directory
    couldn't be found, the test runner will try to create it before
    generate the XML files.
"""

from django.test.simple import *
from django.test.simple import *
from django.test.utils import *
from django.conf import settings
from django.db.models import *
from django.test.simple import build_suite, DjangoTestSuiteRunner
import unittest
import xmlrunner

class XMLTestRunner(DjangoTestSuiteRunner):
    def run_tests(self, test_labels, verbosity=1, interactive=True, extra_tests=[]):
        """
        Run the unit tests for all the test labels in the provided list.
        Labels must be of the form:
         - app.TestClass.test_method
            Run a single specific test method
         - app.TestClass
            Run all the test methods in a given class
         - app
            Search for doctests and unittests in the named application.

        When looking for tests, the test runner will look in the models and
        tests modules for the application.
        
        A list of 'extra' tests may also be provided; these tests
        will be added to the test suite.
        
        Returns the number of tests that failed.
        """
        setup_test_environment()
        
        settings.DEBUG = False
        
        verbose = getattr(settings, 'TEST_OUTPUT_VERBOSE', False)
        descriptions = getattr(settings, 'TEST_OUTPUT_DESCRIPTIONS', False)
        output = getattr(settings, 'TEST_OUTPUT_DIR', '.')
        
        suite = unittest.TestSuite()
        
        if test_labels:
            for label in test_labels:
                if '.' in label:
                    suite.addTest(build_test(label))
                else:
                    app = get_app(label)
                    suite.addTest(build_suite(app))
        else:
            for app in get_apps():
                suite.addTest(build_suite(app))
        
        for test in extra_tests:
            suite.addTest(test)

        old_config = self.setup_databases()

        result = xmlrunner.XMLTestRunner(
            verbose=verbose, descriptions=descriptions, output=output).run(suite)
        
        self.teardown_databases(old_config)

        teardown_test_environment()
        
        return len(result.failures) + len(result.errors)
