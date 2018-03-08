#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging

logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging.DEBUG)
STATES = ['OK', 'WARNING', 'CRITICAL', 'UNKNOWN']


class CheckVariable(object):
    """ class for one single variable to check """

    def __init__(self, name, var_type, unit, ok_condition, warn_condition, crit_condition, pre_processor):
        self.name = name
        self.var_type = var_type
        self.unit = unit
        self.ok_condition = ok_condition
        self.warn_condition = warn_condition
        self.crit_condition = crit_condition
        self.pre_processor = lambda x: x
        if pre_processor:
            self.pre_processor = pre_processor
        self.value = None
        self.check_result = None
        self.nagios_state = STATES.index('UNKNOWN')

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
        try:
            self.value = self.var_type(self.check_result)
            self.value = self.pre_processor(self.value)
        except Exception as e:
            logging.debug("Preprocessor failed: %s" % e)

    def set_state(self):
        if self.value is None:
            return
        evaluations = (self.ok_condition, self.warn_condition, self.crit_condition)
        for state, evaluation in enumerate(evaluations):
            if evaluation and evaluation(self.value):
                self.nagios_state = state
        logging.debug("Variable %s yields nagios state %s" % (self.name, STATES[self.nagios_state]))

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
    def __init__(self, service_name):
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
        logging.debug("adding variable %s (%s)" % (var_name, var_type.__name__))
        if len(self.check_variables) == 0:
            self.main = var_name
        self.check_variables[var_name] = CheckVariable(var_name, var_type, unit, ok_condition,
                                                       warn_condition, crit_condition, pre_processor)

    def add_check_result(self, var_name, check_result):
        variable = self.check_variables.get(var_name)
        if variable is not None:
            logging.debug("Adding check result '%s' to variable %s" % (check_result, var_name))
            variable.set_check_result(check_result)
        else:
            logging.debug("Not knowing variable %s, not adding check result." % var_name)

    def generate_output(self, override_message=None):
        output = ""
        return_code = STATES.index('UNKNOWN')
        for var in self.check_variables.values():
            state = STATES[var.nagios_state]
            if var.name == self.main:
                if override_message:
                    return_code = var.nagios_state
                    output = "%s %s - %s" % (self.service_name, state, override_message.strip())
                elif var.value is not None:
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
