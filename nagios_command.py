#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import sys

# ====================== Configuration ==========================================
commandfile = '/var/lib/nagios3/rw/nagios.cmd'
# ====================== Configuration ==========================================

def read_input(message, default_value=None, result_type=str):
    """ helper function for reading input """
    result = None
    if default_value:
        try:
            result = raw_input("%s [%s]: " % (message, default_value))
        except (KeyboardInterrupt, EOFError):
            sys.exit(0)
        if not result:
            result = default_value
    else:
        while not result:
            try:
                result = raw_input("%s: " % message)
            except (KeyboardInterrupt, EOFError):
                sys.exit(0)
    try:
        result = result_type(result)
    except:
        return None
    return result

commands = {
    'Host and Services downtime': {'command_string': '[%(start)s] SCHEDULE_HOST_DOWNTIME;%(host)s;%(start)s;%(end)s;0;0;%(length)0.0f;nagios console;Reboot\n[%(start)s] SCHEDULE_HOST_SVC_DOWNTIME;%(host)s;%(start)s;%(end)s;0;0;%(length)0.0f;nagios console;Reboot', 'params': ({'name': 'start'}, {'name': 'end'}, {'name': 'length'})},
}
