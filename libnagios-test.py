#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
from libnagios import Nagios, CheckVariable


class NagiosAssetTestCase(unittest.TestCase):

    def setUp(self):
        self.inst = Nagios('Asset')
        ok = lambda x: x > 10
        warn = lambda x: 5 < x <= 10
        crit = lambda x: x <= 5
        asset = CheckVariable('asset', float, 'EUR')
        asset.ok_condition = ok
        asset.warn_condition = warn
        asset.crit_condition = crit
        self.inst.add_check_variable(asset)
        time = CheckVariable('time', float)
        self.inst.add_check_variable(time)

    def run_single_test(self, test):
        for var in test['vars']:
            self.inst.add_check_result(var, test['vars'][var])
        output = self.inst.generate_output()
        self.assertEqual(output, test['expected'])

    def run_multiple_tests(self, tests):
        for test in tests:
            self.inst.clear_results()
            self.run_single_test(test)

    def testOK(self):
        tests = (
            {'vars': {'asset': '12', 'time': '3.9'},
             'expected': (0, 'Asset OK - 12.00 EUR | asset=12.00, time=3.90')},
            {'vars': {'asset': '50.42', 'time': '2.4'},
             'expected': (0, 'Asset OK - 50.42 EUR | asset=50.42, time=2.40')},
        )
        self.run_multiple_tests(tests)

    def testWarning(self):
        tests = (
            {'vars': {'asset': '5.1', 'time': '3.9'},
             'expected': (
                 1, 'Asset WARNING - 5.10 EUR | asset=5.10, time=3.90')},
            {'vars': {'asset': '7', 'time': '2.4'},
             'expected': (
                 1, 'Asset WARNING - 7.00 EUR | asset=7.00, time=2.40')},
            {'vars': {'asset': '10'},
             'expected': (1, 'Asset WARNING - 10.00 EUR | asset=10.00')},
        )
        self.run_multiple_tests(tests)

    def testCritical(self):
        tests = (
            {'vars': {'asset': '5', 'time': '3.9'},
             'expected': (
                 2, 'Asset CRITICAL - 5.00 EUR | asset=5.00, time=3.90')},
            {'vars': {'asset': '2', 'time': '2.4'},
             'expected': (
                 2, 'Asset CRITICAL - 2.00 EUR | asset=2.00, time=2.40')},
            {'vars': {'asset': '-10'},
             'expected': (2, 'Asset CRITICAL - -10.00 EUR | asset=-10.00')},
        )
        self.run_multiple_tests(tests)

    def testUnknown(self):
        tests = (
            {'vars': {'asset': 'a', 'time': '3.9'},
             'expected': (3, 'Asset UNKNOWN - None | time=3.90')},
            {'vars': {'time': '2.4'},
             'expected': (3, 'Asset UNKNOWN - None | time=2.40')},
            {'vars': {None: 'useless'},
             'expected': (3, 'Asset UNKNOWN - None')},
        )
        self.run_multiple_tests(tests)

    def testOverride(self):
        message = 'override message'
        expected = (3, 'Asset UNKNOWN - override message')
        output = self.inst.generate_output(override_message=message)
        self.assertEqual(output, expected)


if __name__ == '__main__':
    unittest.main()
