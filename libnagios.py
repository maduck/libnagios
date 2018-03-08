#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
import aenum

logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging.WARN)
States = aenum.Enum('States', 'OK WARNING CRITICAL UNKNOWN', start=0)


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
        self.nagios_state = States.UNKNOWN

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
        state = States.UNKNOWN
        for state, evaluation in enumerate(evaluations):
            if evaluation and evaluation(self.value):
                self.nagios_state = States(state)
        logging.debug("Variable %s yields nagios state %r" % (self.name, state))

    def pretty_format(self):
        result = str(self)
        if self.unit and self.value is not None:
            result = "%s %s" % (result, self.unit)
        return result

    def __str__(self):
        result = "%s" % self.value
        if self.var_type == float and self.value is not None:
            result = "%0.2f" % self.value
        return result


class Nagios(object):
    def __init__(self, service_name):
        self.service_name = service_name
        self.check_variables = {}
        self.check_result = States.UNKNOWN
        self.main = None

    def clear_results(self):
        """
            removes any results so you can re-use this object
        """
        self.check_result = States.UNKNOWN
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

    def generate_performance_data(self):
        performance_datapoints = []
        output = ""
        for var in self.check_variables.values():
            if var.has_perfdata():
                performance_datapoints.append(var.get_perfdata())
        if performance_datapoints:
            output = " | %s" % ", ".join(performance_datapoints)
        return output

    def generate_return_code(self):
        state = States.UNKNOWN
        output = ""
        for var in self.check_variables.values():
            if var.name == self.main:
                state = var.nagios_state
                output = var.pretty_format()
        return state.value, output

    def generate_output(self, override_message=None):
        return_code, var_output = self.generate_return_code()
        state = States(return_code).name
        output = "%s %s - %s" % (self.service_name, state, var_output)
        if override_message is not None:
            output = "%s %s - %s" % (self.service_name, state, override_message.strip())
        output += self.generate_performance_data()
        return return_code, output
