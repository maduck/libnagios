#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import argparse

parser = argparse.ArgumentParser(
    description="Schedule a downtime for a host and all of its services.")
parser.add_argument("--hosts", "-H", nargs="+", required=True,
                    help="list of hosts to schedule a downtime for")
parser.add_argument("--duration", "-D", type=int, default=2,
                    help="Downtime duration, defaults to %(default)d")
parser.add_argument("--commandfile", "-c", type=argparse.FileType('a'),
                    default="/var/lib/nagios3/rw/nagios.cmd",
                    help="Nagios command file, defaults to %(default)s")


args = parser.parse_args()

downtime_length = float(args.duration) * 60 * 60
downtime_start = time.time()
downtime_end = downtime_start + downtime_length

host_downtime = "[{}] SCHEDULE_HOST_DOWNTIME".format(downtime_start)
service_downtime = "[{}] SCHEDULE_HOST_SVC_DOWNTIME".format(downtime_start)


for host in args.hosts:
    nagios_parameters = [
        host,
        "{:0.0f}".format(downtime_start),
        "{:0.0f}".format(downtime_end),
        "0",
        "0",
        "{:0.0f}".format(downtime_length),
        "libnagios",
        "CLI command\n",
    ]

    args.commandfile.write(";".join([host_downtime] + nagios_parameters))
    args.commandfile.write(";".join([service_downtime] + nagios_parameters))
