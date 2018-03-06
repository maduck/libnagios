.. image:: https://img.shields.io/travis/maduck/libnagios.svg?style=flat-square
   :target: https://travis-ci.org/maduck/libnagios
   :alt: Travis 

.. image:: https://img.shields.io/coveralls/github/maduck/libnagios.svg?style=flat-square
   :alt: Coveralls
   :target: https://coveralls.io/github/maduck/libnagios

.. image:: https://landscape.io/github/maduck/libnagios/master/landscape.svg?style=flat-square
   :target: https://landscape.io/github/maduck/libnagios/master
   :alt: Code Health

.. image:: https://img.shields.io/codacy/grade/e27821fb6289410b8f58338c7e0bc686.svg?style=flat-square
   :target: https://www.codacy.com/app/maduck/libnagios
   :alt: Codacy grade

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
