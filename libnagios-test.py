#!/usr/bin/python
# -*- coding: utf-8 -*-

from libnagios import nagios

# initialize nagios instance
inst = nagios('Asset', debug=False)

# first variable is the one which will be evaluated
inst.add_check_variable('asset', float, "EUR", lambda x: x > 10, lambda x: x > 5 and x <= 10, lambda x: x <= 5)
# second variable does not need to have additional information, thus always returns status 'OK'
inst.add_check_variable('time', float)

# give check results to instance, it will be evaluated
inst.add_check_result('asset', 'a')
inst.add_check_result('time', '3.9')

# return nagios compatible output
output = inst.generate_output()

print "Checking output: ", repr(output)
assert(output == (3, 'Asset UNKNOWN | time=3.90'))
