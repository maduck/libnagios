#!/usr/bin/python
# -*- coding: utf-8 -*-

STATES = ['OK', 'WARNING', 'CRITICAL', 'UNKNOWN']

class CheckVariable(object):
    """ class for one single variable to check """

    def __init__(self, name, var_type, unit, ok_condition, warn_condition, crit_condition, pre_processor, debug):
        self.name = name
        self.var_type = var_type
        self.unit = unit
        self.ok_condition = ok_condition
        self.warn_condition = warn_condition
        self.crit_condition = crit_condition
        self.pre_processor = pre_processor
        self.nagios_state = STATES.index('UNKNOWN')
        self.debug = debug

    def has_check_result(self):
        return hasattr(self, 'check_result')

    def has_value(self):
        return hasattr(self, 'value')

    def get_value(self):
        if self.has_value():
            try:
                return self.value
            except:
                import pdb
                pdb.set_trace()
        else:
            return None

    def clear(self):
        """ resets the former results """
        if self.has_check_result():
            del self.check_result
        if self.has_value():
            del self.value

    def set_check_result(self, check_result):
        self.check_result = check_result
        self.process()
        self.set_state()

    def process(self):
        if self.check_result:
            try:
                self.value = self.var_type(self.check_result)
                if self.pre_processor:
                    self.value = self.pre_processor(self.value)
                    if self.debug:
                        print "[DEBUG] Running Preprocessor on variable %s, new value: %s" % (self.name, self.value)
            except Exception:
                pass

    def set_state(self):
        if self.has_value():
            if self.ok_condition(self.value):
                self.nagios_state = STATES.index('OK')
            elif self.warn_condition(self.value):
                self.nagios_state = STATES.index('WARNING')
            elif self.crit_condition(self.value):
                self.nagios_state = STATES.index('CRITICAL')
        if self.debug:
            print "[DEBUG] Variable %s yields nagios state %s" % (self.name, STATES[self.nagios_state])

class Nagios(object):
    def __init__(self, service_name, debug=False):
        self.debug = debug
        self.service_name = service_name
        self.check_variables = []
        self.check_result = 3
        self.performance_data = []
        self.main = None

    def clear_results(self):
        """
            removes any results so you can re-use this object
        """
        self.check_result = 3
        self.performance_data = []
        for variable in self.check_variables:
            variable.clear()

    def add_check_variable(self, var_name, var_type, unit='', ok_condition=lambda x: True, warn_condition=None, crit_condition=None, pre_processor=None):
        if self.debug:
            print "[DEBUG] adding variable %s (%s)" % (var_name, var_type.__name__)
        if len(self.check_variables) == 0:
            self.main = var_name
        self.check_variables.append(CheckVariable(var_name, var_type, unit, ok_condition, warn_condition, crit_condition, pre_processor, self.debug))

    def __get_variable(self, name):
        for i, variable in enumerate(self.check_variables):
            if variable.name == name:
                return i
        return None

    def add_check_result(self, var_name, check_result):
        variable = self.__get_variable(var_name)
        if variable is not None:
            if self.debug:
                print "[DEBUG] Adding check result '%s' to variable %s" % (check_result, var_name)
            self.check_variables[variable].set_check_result(check_result)
        else:
            if self.debug:
                print "[DEBUG] Not knowing variable %s, not adding check result." % var_name
            return

    def __format_single_number(self, number, var_type):
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
                code = STATES.index('UNKNOWN')
                for var in self.check_variables:
                    state = STATES[var.nagios_state]
                    result = self.__format_single_number(var.get_value(), var.var_type)
                    if result and state != 'UNKNOWN':
                        if var.name == self.main:
                            code = var.nagios_state
                            if var.unit:
                                output = "%s %s - %s %s" % (self.service_name, state, result, var.unit)
                            else:
                                output = "%s %s - %s" % (self.service_name, state, result)
                        if var.var_type != str:
                                self.performance_data.append('%s=%s' % (var.name, result))
                    elif message and var.name == self.main:
                        code = var.nagios_state
                        output = "%s %s - %s" % (self.service_name, state, message.strip())
                    elif var.name == self.main:
                        code = var.nagios_state
                        output = "%s %s" % (self.service_name, state)
                if len(self.performance_data) > 0:
                        output += " | %s" % ", ".join(self.performance_data)
                return (code, output)
