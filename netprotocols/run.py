"""
CLI for managing test scripts
"""

import sys
from argparse import ArgumentParser

from test_cases import (
    lldp_ctl, telnet_ctl,
    ssh_ctl, ipv4_6_ctl,
    dip_ctl, net_ports_ctl,
    reset_ctl, rtc_ctl,
    syslog_ctl, ssl_ctl,
    snmp_ctl
)

from netmiko.exceptions import (
    NetmikoTimeoutException,
    NetMikoAuthenticationException,
    ConnectionException,
    ReadException,
    WriteException,
    NetmikoBaseException
)


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
    return parse.parse_args()


def run() -> None:
    """ Run all or specified tests """
    try:
        args = parser()
        if args.all:
            [print(func()) for func in [ lldp_ctl, telnet_ctl,
                                        ssh_ctl, ipv4_6_ctl,
                                        dip_ctl, net_ports_ctl,
                                        reset_ctl, rtc_ctl,
                                        syslog_ctl, ssl_ctl,
                                        snmp_ctl
                                    ]
                                ]
        else:
            if args.lldp:
                print(lldp_ctl())
            if args.telnet:
                print(telnet_ctl())
            if args.ssh:
                print(ssh_ctl())
            if args.ipv:
                ipv4_6_ctl()
            if args.dip:
                dip_ctl()
            if args.ports:
                net_ports_ctl()
            if args.reset:
                reset_ctl()
            if args.rtc:
                rtc_ctl()
            if args.syslog:
                syslog_ctl()
            if args.ssl:
                ssl_ctl()
            if args.snmp:
                snmp_ctl()

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
