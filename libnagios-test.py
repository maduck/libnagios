#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
from libnagios import Nagios

class NagiosAssetTestCase(unittest.TestCase):

    def setUp(self):
        # initialize nagios instance
        self.inst = Nagios('Asset', debug=False)
        self.inst.add_check_variable('asset', float, "EUR", lambda x: x > 10, lambda x: x > 5 and x <= 10, lambda x: x <= 5)
        self.inst.add_check_variable('time', float)

    def run_single_test(self, test):
        for var in test['vars']:
            self.inst.add_check_result(var, test['vars'][var])
        output = self.inst.generate_output()
        self.assertEquals(output, test['expected'])

    def run_multiple_tests(self, tests):
        for test in tests:
            self.inst.clear_results()
            self.run_single_test(test)

    def testOK(self):
        tests = (
            {'vars': {'asset': '12', 'time': '3.9'}, 'expected': (0, 'Asset OK - 12.00 EUR | asset=12.00, time=3.90')},
            {'vars': {'asset': '50.42', 'time': '2.4'}, 'expected': (0, 'Asset OK - 50.42 EUR | asset=50.42, time=2.40')},
        )
        self.run_multiple_tests(tests)

    def testWarning(self):
        tests = (
            {'vars': {'asset': '5.1', 'time': '3.9'}, 'expected': (1, 'Asset WARNING - 5.10 EUR | asset=5.10, time=3.90')},
            {'vars': {'asset': '7', 'time': '2.4'}, 'expected': (1, 'Asset WARNING - 7.00 EUR | asset=7.00, time=2.40')},
            {'vars': {'asset': '10'}, 'expected': (1, 'Asset WARNING - 10.00 EUR | asset=10.00')},
        )
        self.run_multiple_tests(tests)

    def testCritical(self):
        tests = (
            {'vars': {'asset': '5', 'time': '3.9'}, 'expected': (2, 'Asset CRITICAL - 5.00 EUR | asset=5.00, time=3.90')},
            {'vars': {'asset': '2', 'time': '2.4'}, 'expected': (2, 'Asset CRITICAL - 2.00 EUR | asset=2.00, time=2.40')},
            {'vars': {'asset': '-10'}, 'expected': (2, 'Asset CRITICAL - -10.00 EUR | asset=-10.00')},
        )
        self.run_multiple_tests(tests)

    def testUnknown(self):
        tests = (
            {'vars': {'asset': 'a', 'time': '3.9'}, 'expected': (3, 'Asset UNKNOWN | time=3.90')},
            {'vars': {'time': '2.4'}, 'expected': (3, 'Asset UNKNOWN | time=2.40')},
            {'vars': {}, 'expected': (3, 'Asset UNKNOWN')},
        )
        self.run_multiple_tests(tests)

if __name__ == '__main__':
    unittest.main()
