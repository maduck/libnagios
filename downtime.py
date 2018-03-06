#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
# ====================== Configuration ==========================================
command_file = '/var/lib/nagios3/rw/nagios.cmd'
# ====================== Configuration ==========================================

hosts = input("Hostnames, comma delimited").split(',')
downtime_length = input("Länge der Downtime in Stunden")
if not downtime_length:
    downtime_length = 2
downtime_length = float(downtime_length) * 60 * 60
downtime_start = time.time()
downtime_end = downtime_start + downtime_length

for host in hosts:
    params = (downtime_start, host, downtime_start, downtime_end, downtime_length)
    print("[%s] SCHEDULE_HOST_DOWNTIME;%s;%s;%s;0;0;%0.0f;nagios console;Reboot" % params)
    print("[%s] SCHEDULE_HOST_SVC_DOWNTIME;%s;%s;%s;0;0;%0.0f;nagios console;Reboot" % params)
