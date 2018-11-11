.. image:: https://img.shields.io/travis/maduck/libnagios.svg?style=flat-square
   :target: https://travis-ci.org/maduck/libnagios
   :alt: Travis 

.. image:: https://img.shields.io/coveralls/github/maduck/libnagios.svg?style=flat-square
   :alt: Coveralls
   :target: https://coveralls.io/github/maduck/libnagios

.. image:: https://landscape.io/github/maduck/libnagios/master/landscape.svg?style=flat-square
   :target: https://landscape.io/github/maduck/libnagios/master
   :alt: Code Health

.. image:: https://img.shields.io/codacy/grade/bbf4f311bc9246b5b07df02e4d7f39e5.svg?style=flat-square
   :target: https://www.codacy.com/app/maduck/libnagios
   :alt: Codacy grade

.. image:: https://api.codeclimate.com/v1/badges/cbe1003f499631f2729c/maintainability
   :target: https://codeclimate.com/github/maduck/libnagios/maintainability
   :alt: Maintainability

Nagios plugin helper library. It is now easy to write Nagios plugins in python without bothering with details.

An example::

  import sys
  from libnagios import Nagios

  nagios_check = Nagios('Asset')

  asset = CheckVariable('asset', float, 'EUR')
  asset.ok_condition = lambda x: x > 10
  asset.warn_condition = lambda x: 5 < x <= 10
  asset.crit_condition = lambda x: x <= 5
  self.inst.add_check_variable(asset)

  nagios_check.add_check_variable(asset)
  
  nagios_check.add_check_result('asset', 12)
  code, output = nagios_check.generate_output()

  print(output)
  sys.exit(code)

this should print 'Asset OK - 12.00 EUR | asset=12.00', and exit with code '0'.
