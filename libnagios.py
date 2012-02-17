#!/usr/bin/python
# -*- coding: utf-8 -*-

class nagios():
    OK = 0
    WARNING = 1
    CRITICAL = 2
    UNKNOWN = 3

    def __init__(self, service_name, debug=False):
        self.states = ('OK', 'WARNING', 'CRITICAL', 'UNKNOWN')

        self.debug = debug
        self.service_name = service_name
        self.check_variables = {}
        self.check_result = 3
        self.performance_data = []
        self.main = None

    def clear_results(self):
        """
            removes any results so you can re-use this object
        """

        self.check_result = 3
        self.performance_data = []
        for var_name in self.check_variables:
            if 'check_result' in self.check_variables[var_name]:
                del self.check_variables[var_name]['check_result']
            if 'value' in self.check_variables[var_name]:
                del self.check_variables[var_name]['value']

    def add_check_variable(self, var_name, var_type, unit='', ok_condition=lambda x: True, warn_condition=None, crit_condition=None, pre_processor=None):
        if self.debug:
            print "DEBUG: adding variable %s (%s)" % (var_name, var_type.__name__)
        if len(self.check_variables) == 0:
            self.main = var_name
        self.check_variables.update({var_name: {
            'var_type': var_type,
            'unit': unit,
            'ok_condition': ok_condition,
            'warn_condition': warn_condition,
            'crit_condition': crit_condition,
            'nagios_state': self.UNKNOWN,
            'pre_processor': pre_processor,
        }})

    def add_check_result(self, var_name, check_result):
        if self.check_variables and var_name in self.check_variables:
            self.check_variables[var_name]['check_result'] = check_result
            if self.debug:
                print "DEBUG: Adding check result '%s' to variable %s" % (check_result, var_name)
        elif self.debug:
            print "DEBUG: Not knowing variable %s, not adding check result." % var_name
        value = None
        try:
            value = self.check_variables[var_name]['var_type'](self.check_variables[var_name]['check_result'])
            if self.check_variables[var_name]['pre_processor']:
                value = self.check_variables[var_name]['pre_processor'](value)
                if self.debug:
                    print "DEBUG: Running Preprocessor on variable %s, new value: %s" % (var_name, value)
        except:
            pass
        self.check_variables[var_name]['value'] = value
        if value:
            if self.check_variables[var_name]['ok_condition'](value):
                self.check_variables[var_name]['nagios_state'] = self.OK
            elif self.check_variables[var_name]['warn_condition'](value):
                self.check_variables[var_name]['nagios_state'] = self.WARNING
            elif self.check_variables[var_name]['crit_condition'](value):
                self.check_variables[var_name]['nagios_state'] = self.CRITICAL
            else:
                self.check_variables[var_name]['nagios_state'] = self.UNKNOWN
        else:
            self.check_variables[var_name]['nagios_state'] = self.UNKNOWN
        if self.debug:
            print "DEBUG: Variable %s yields nagios state %s" % (var_name, self.states[self.check_variables[var_name]['nagios_state']])

    def _format_single_number(self, number, var_type):
        if number:
            try:
                if var_type in (float, long):
                    return "%0.2f" % number
                elif var_type == int:
                    return "%d" % number
                else:
                    return "%s" % number
            except:
                return "%s" % number
        else:
            return None

    def generate_output(self, message=None):
                output = ""
                code = self.UNKNOWN
                for var_name, variable in self.check_variables.items():
                        state = self.states[variable['nagios_state']]
                        result = self._format_single_number(variable['value'] if 'value' in variable else None, variable['var_type'])
                        if result and state != 'UNKNOWN':
                                if var_name == self.main:
                                        code = variable['nagios_state']
                                        if variable['unit']:
                                                output = "%s %s - %s %s" % (self.service_name, state, result, variable['unit'])
                                        else:
                                                output = "%s %s - %s" % (self.service_name, state, result)
                                if variable['var_type'] != str:
                                        self.performance_data.append('%s=%s' % (var_name, result))
                        elif message and var_name == self.main:
                                code = variable['nagios_state']
                                output = "%s %s - %s" % (self.service_name, state, message.strip())
                        elif var_name == self.main:
                                code = variable['nagios_state']
                                output = "%s %s" % (self.service_name, state)
                if len(self.performance_data) > 0:
                        output += " | %s" % ", ".join(self.performance_data)
                return (code, output)
