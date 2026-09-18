#!/usr/bin/env python3

"""
CLI for managing test scripts
"""

import sys
import pathlib
from argparse import ArgumentParser

from netmiko.exceptions import (
    NetmikoTimeoutException,
    NetMikoAuthenticationException,
    ConnectionException,
    ReadException,
    WriteException,
    NetmikoBaseException
)

try:
    for module in ['common', 'net_protocols', 'poe', 'scripts']:
        sys.path.append(str(pathlib.Path(module)))

    import net_protocols.test_cases as tc
    from poe.test_poe import poe_ctl

except ModuleNotFoundError as e:
    print(f"{__file__}: {e}")
    sys.exit(1)


def parser():
    """ Parsing command line arguments """
    parse = ArgumentParser()
    # validate flags
    parse.add_argument('--all', action='store_true',
                       help='Run all Test-Cases')
    parse.add_argument('--lldp', action='store_true',
                       help='Print neighbor information')
    parse.add_argument('--telnet', action='store_true',
                       help='Test Telnet connection')
    parse.add_argument('--ssh', action='store_true',
                       help='Test SSH connection')
    parse.add_argument('--reset', action='store_true',
                       help='Test Reset settings to default')
    parse.add_argument('--ipv', action='store_true',
                       help='Checking ipv4/6 protocol support')
    parse.add_argument('--dip', action='store_true',
                       help='Checking the functionality of the DIP switch')
    parse.add_argument('--ports', action='store_true',
                       help='Check the switch network port indicator')
    parse.add_argument('--rtc', action='store_true',
                       help='Checking support reading time from RTC')
    parse.add_argument('--syslog', action='store_true',
                       help='Testing the logging system')
    parse.add_argument('--ssl', action='store_true',
                       help='Test SSL certification support')
    parse.add_argument('--snmp', action='store_true',
                       help='Testing support SNMP protocol')
    parse.add_argument('--temp', action='store_true',
                       help='Temperature sensor testing')
    parse.add_argument('--poe', action='store_true',
                       help='PoE chip testing')
    return parse.parse_args()


def run() -> None:
    """ Run all or specified tests """
    try:
        args = parser()
        if args.all:
            for func in [ tc.ssh_ctl, tc.telnet_ctl, tc.lldp_ctl, tc.ipv4_6_ctl,
                         tc.syslog_ctl, tc.ssl_ctl, tc.snmp_ctl, tc.temp_ctl, ]:
                print(func())
        else:
            if args.lldp:
                print(tc.lldp_ctl())
            if args.telnet:
                print(tc.telnet_ctl())
            if args.ssh:
                print(tc.ssh_ctl())
            if args.ipv:
                tc.ipv4_6_ctl()
            if args.dip:
                tc.dip_ctl()
            if args.ports:
                tc.net_ports_ctl()
            if args.reset:
                tc.reset_ctl()
            if args.rtc:
                tc.rtc_ctl()
            if args.syslog:
                tc.syslog_ctl()
            if args.ssl:
                tc.ssl_ctl()
            if args.snmp:
                tc.snmp_ctl()
            if args.temp:
                tc.temp_ctl()
            if args.poe:
                poe_ctl()

    except NetmikoTimeoutException:
        print('SSH session timed trying to connect to the device')
    except NetMikoAuthenticationException:
        print('SSH authentication exception based on Paramiko AuthenticationException')
    except ConnectionException:
        print('Generic exception indicating the connection failed')
    except (ReadException, WriteException):
        print('An error occurred during a read or write operation')
    except NetmikoBaseException:
        print('Possible errors are related with:\n' \
                ' Generic exception indicating the connection failed\n' \
                ' Exception raised for invalid configuration error\n' \
                ' General exception indicating an error occurred during a Netmiko write operation\n'
            )
    finally:
        sys.exit()


if __name__ == '__main__':
    run()
