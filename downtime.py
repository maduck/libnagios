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
        except KeyboardInterrupt:
            sys.exit(0)
        except (KeyboardInterrupt, EOFError):
            pass
        if not result:
            result = default_value
    else:
        while not result:
            try:
                result = raw_input("%s: " % message)
            except KeyboardInterrupt:
                sys.exit(0)
            except (KeyboardInterrupt, EOFError):
                pass
    try:
        result = result_type(result)
    except:
        return None
    return result

hosts = read_input("Hostname, durch Komma getrennt").split(',')
downtime_length = read_input("Länge der Downtime in Stunden", 2, float) * 60 * 60
downtime_start = time.time()
downtime_end = downtime_start + downtime_length


#/usr/bin/printf "[%lu] SCHEDULE_HOST_DOWNTIME;%s;%lu;%lu;0;0;7200;nagios console;Reboot\n" $now $host $now $then > $commandfile
#/usr/bin/printf "[%lu] SCHEDULE_HOST_SVC_DOWNTIME;%s;%lu;%lu;0;0;7200;nagios console;Reboot\n" $now $host $now $then > $commandfile

for host in hosts:
    print "[%s] SCHEDULE_HOST_DOWNTIME;%s;%s;%s;0;0;%0.0f;nagios console;Reboot" % (downtime_start, host, downtime_start, downtime_end, downtime_length)
    print "[%s] SCHEDULE_HOST_SVC_DOWNTIME;%s;%s;%s;0;0;%0.0f;nagios console;Reboot" % (downtime_start, host, downtime_start, downtime_end, downtime_length)
