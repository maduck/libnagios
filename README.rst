Nagios plugin helper library. It is now easy to write Nagios plugins in python without bothering with details.

An example::
  import sys
  from libnagios import Nagios

  self.inst = Nagios('Asset')
  self.inst.add_check_variable('asset', float, "EUR", lambda x: x > 10, lambda x: x > 5 and x <= 10, lambda x: x <= 5)
  
  self.inst.add_check_result('asset', 12)
  code, output = self.inst.generate_output()

  print(output)
  sys.exit(code)

this should print 'Asset OK - 12.00 EUR', and exit with code '0'.
