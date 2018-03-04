.. image:: https://img.shields.io/travis/maduck/libnagios.svg?style=for-the-badge
    :alt: Travis
.. image:: https://img.shields.io/coveralls/github/maduck/libnagios.svg?style=for-the-badge
    :alt: Coveralls github

Nagios plugin helper library. It is now easy to write Nagios plugins in python without bothering with details.

An example::

  import sys
  from libnagios import Nagios

  nagios_check = Nagios('Asset')
  nagios_check.add_check_variable('asset', float, "EUR", lambda x: x > 10, lambda x: x > 5 and x <= 10, lambda x: x <= 5)
  
  nagios_check.add_check_result('asset', 12)
  code, output = nagios_check.generate_output()

  print(output)
  sys.exit(code)

this should print 'Asset OK - 12.00 EUR', and exit with code '0'.
