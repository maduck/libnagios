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
        self.value = None
        self.check_result = None
        self.nagios_state = STATES.index('UNKNOWN')
        self.debug = debug

    def has_check_result(self):
        return self.check_result is not None

    def has_value(self):
        return self.value is not None

    def get_value(self):
        if self.has_value():
            return self.value

    def has_perfdata(self):
        return self.value is not None and self.var_type in (float, int)

    def get_perfdata(self):
        return "%s=%0.2f" % (self.name, self.value)

    def clear(self):
        """ resets the former results """
        self.check_result = None
        self.value = None

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
                        print("[DEBUG] Running Preprocessor on variable %s, new value: %s" % (self.name, self.value))
            except Exception as e:
                if self.debug:
                    print("[DEBUG] Preprocessor failed: %s" % e)

    def set_state(self):
        if self.has_value():
            if self.ok_condition(self.value):
                self.nagios_state = STATES.index('OK')
            elif self.warn_condition(self.value):
                self.nagios_state = STATES.index('WARNING')
            elif self.crit_condition(self.value):
                self.nagios_state = STATES.index('CRITICAL')
        if self.debug:
            print("[DEBUG] Variable %s yields nagios state %s" % (self.name, STATES[self.nagios_state]))

    def pretty_format(self):
        result = str(self)
        if self.unit:
            result = "%s %s" % (result, self.unit)
        return result

    def __str__(self):
        result = "%s" % self.value
        if self.var_type == float:
            result = "%0.2f" % self.value
        return result


class Nagios(object):
    def __init__(self, service_name, debug=False):
        self.debug = debug
        self.service_name = service_name
        self.check_variables = {}
        self.check_result = STATES.index('UNKNOWN')
        self.performance_data = []
        self.main = None

    def clear_results(self):
        """
            removes any results so you can re-use this object
        """
        self.check_result = STATES.index('UNKNOWN')
        self.performance_data = []
        for variable in self.check_variables.values():
            variable.clear()

    def add_check_variable(self, var_name, var_type, unit='', ok_condition=lambda x: True, warn_condition=None,
                           crit_condition=None, pre_processor=None):
        if self.debug:
            print("[DEBUG] adding variable %s (%s)" % (var_name, var_type.__name__))
        if len(self.check_variables) == 0:
            self.main = var_name
        self.check_variables[var_name] = CheckVariable(var_name, var_type, unit, ok_condition,
                                                       warn_condition, crit_condition, pre_processor, self.debug)

    def add_check_result(self, var_name, check_result):
        variable = self.check_variables.get(var_name)
        if variable is not None:
            if self.debug:
                print("[DEBUG] Adding check result '%s' to variable %s" % (check_result, var_name))
            variable.set_check_result(check_result)
        else:
            if self.debug:
                print("[DEBUG] Not knowing variable %s, not adding check result." % var_name)

    def generate_output(self, override_message=None):
        output = ""
        return_code = STATES.index('UNKNOWN')
        for var in self.check_variables.values():
            state = STATES[var.nagios_state]
            if var.name == self.main:
                if override_message:
                    return_code = var.nagios_state
                    output = "%s %s - %s" % (self.service_name, state, override_message.strip())
                elif var.has_value():
                    return_code = var.nagios_state
                    output = "%s %s - %s" % (self.service_name, state, var.pretty_format())
                else:
                    return_code = var.nagios_state
                    output = "%s %s" % (self.service_name, state)
            if var.has_perfdata():
                self.performance_data.append(var.get_perfdata())
        if self.performance_data:
            output += " | %s" % ", ".join(self.performance_data)
        return return_code, output
