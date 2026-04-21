"""
Test objects
"""

import sys
import subprocess as sp
from os import getcwd
from time import sleep
from datetime import datetime
from typing import (
    List,
    LiteralString,
    Union,
    Callable,
    Any
)
from dataclasses import dataclass

# custom libs
from data import RemoteConnection
from auth_and_basequery_via_api import base_query, EndPoints
from exceptions import (
    CommandNotFound,
    ResetModeNotSelected,
    ShortPeriodOfTimeToConnect,
)


class IPv:
    """
    Checking ipv4/6 protocol support
    """
    @staticmethod
    def check_ip_protocol_version(host: str) -> list[str]:
        """ Сhecking IP address in version 4/6. """
        try:
            for isdigite in host:
                if isdigite == '.':
                    continue
                int(isdigite)
            clear_ip_stat = 'clear ip statistics'
            show_ip_stat = 'show ip statistics'
            ping = f'ping -4 -c 10 {host}'
        except ValueError:
            clear_ip_stat = 'clear ipv6 statistics'
            show_ip_stat = 'show ipv6 statistics interface vlan 1'
            ping = f'ping -6 -c 10 {host}'

        return [clear_ip_stat, show_ip_stat, ping]

    @staticmethod
    def clear_ip_statistics(command, ssh_session) -> None:
        """ Сlears statistics of transmitted packets. """
        ssh_session.send_command(command)

    @staticmethod
    def icmp_request(command) -> None:
        """ Checking support protocol IP version 4/6. """
        sp.run(command.split(), check=True)

    @staticmethod
    def output_ip_statistics(command, ssh_session) -> None:
        """ Displays current statistics of transmitted packets. """
        print(ssh_session.send_command(command) + '\n')


class LLDP:
    """
    Checking the support of the LLDP protocol in the Switch
    """
    @staticmethod
    def get_lldp_from_client() -> Union[str, None]:
        """ Returns info about Client [ interface, portDescr, mac and etc...] """
        command: List[LiteralString] = 'sudo lldpcli show neighbors'.split()
        try:
            raw = sp.run(command, capture_output=True, text=True, check=True, encoding='utf8')
            return ' Client Info:\n' + raw.stdout
        except sp.CalledProcessError:
            print('Command execution error')
        except FileNotFoundError:
            print(f'Command {command} not found')

        return None

    @staticmethod
    def get_lldp_from_switch() -> Union[str, None]:
        """ Returns info about Switch [ local interface, mac, portDescr and etc...] """
        command: str = 'show lldp neighbors'
        with RemoteConnection().init_conn_session() as ssh_conn:
            return 'Switch Info:\n' + str(ssh_conn.send_command(command))


class SSHConnect():
    """
    Checking SSH connection support on the Switch
    Also:
    Provides services for activation/deactivation
    and verification of connections via ssh.
    """
    @staticmethod
    def is_enabled(output: str) -> bool:
        """ Checking ssh connection activity """
        can_active: str = 'enabled'
        return can_active in output

    @staticmethod
    def get_info_about_ssh(tn_connect) -> str:
        """ Get information about the presence of a connection via ssh """
        mode: str = 'do show ip ssh'
        output: str = tn_connect.send_command(mode).split()
        return output

    @staticmethod
    def activate(tn_connect) -> None:
        """ Activate ssh connection """
        enable_ssh_connection: list[str] = ['ip ssh']
        tn_connect.send_config_set(enable_ssh_connection)

    @staticmethod
    def deactivate(tn_connect) -> None:
        """ Deactivate ssh connection """
        disable_ssh_connection: list[str] = ['no ip ssh']
        tn_connect.send_config_set(disable_ssh_connection)


class NetPorts:
    """
    Checking the indication of the switch network ports
    """
    @staticmethod
    def checking_switch_availability(host: str) -> bool:
        """ Checks the availability of the switch. """
        ping: list[str] = f'ping -c 4 {host}'.split()
        status_code: int = sp.run(ping, check=True).returncode
        if not status_code:
            sleep(10)
            return True

        return False

    @staticmethod
    def generate_icmp_packets(host: str) -> None:
        """ Generates icmp network packets to send them to switch ports. """
        ping: list[str] = f'ping {host}'.split()
        sp.run(ping, check=True)


class ResetButton:
    """
    Checking for a return to default settings
    """
    @staticmethod
    def run_commands_context_conn_session(ssh_conn: Any = "") -> Callable:
        """ Executing commands in a specific connection session """
        def execute_commands(command: Union[str, None] = None,
                            config_commands: Union[List[str], None] = None
                        ) -> Any:
            """ Runs commands on the switch """
            if command is not None:
                return ssh_conn.send_command(command)
            if config_commands is not None:
                return ssh_conn.send_config_set(config_commands)
            raise CommandNotFound('Сommand was not passed !')
        return execute_commands

    @staticmethod
    def isadded_vlan(output: Any) -> bool:
        """ Check previously created vlan """
        strings: List[str] = str(output).split()
        for string in strings:
            if string == 'VLAN0010':
                return True
        return False

    @staticmethod
    def do_reconnect(short_reset: bool = False,
                    long_reset: bool = False,
                    wait_for_reconnect: int = 0
                ) -> None:
        """ Re-establishing SSH connection """
        mode: str = ""
        if short_reset:
            mode = 'SOFT Reset'
        elif long_reset:
            mode = 'HARD Reset'
        else:
            raise ResetModeNotSelected('One of the reset modes is not selected !')

        if wait_for_reconnect >= 120:
            print(f'Connect aborting ... reconnect after {wait_for_reconnect}s Use {mode} !\n')
            sleep(wait_for_reconnect)
        else:
            raise ShortPeriodOfTimeToConnect('Required time to connect 120 seconds or more !')


class RTC:
    """
    Checking support reading time from RTC
    """
    @staticmethod
    def configure_datetime(ssh_conn: Any, flag: str = "") -> str:
        """
        Set time on Switch
        and return datetime
        """
        if flag == 'set_dt':
            print('Setting time on Switch ...')
            sleep(3)
            config_commands: list[str] = [
                "clock time \
                day 01 month 01 year 2023 \
                hour 00 minute 00 second 00"
            ]
            ssh_conn.send_config_set(config_commands=config_commands)

        return str(ssh_conn.send_command('show clock')).split()[-1]

    @staticmethod
    def convert_datetime_to_unix(dt: str = "", seconds: int = 0) -> int:
        """ Date and time to Unix epoch """
        try:
            date: str = dt[:dt.index('T')]
            time: str = dt[dt.index('T') + 1:dt.index('+')]
            seconds = int(datetime.strptime(f'{date} {time}', '%Y-%m-%d %H:%M:%S').timestamp())
            return seconds
        except ValueError:
            print('Error converting date and time to unix !')
            sys.exit(1)

    @staticmethod
    def counter_time() -> int:
        """ Counting the time elapsed """
        try:
            print('To stop timer and continue test press Ctrl+C')
            secs: int = 0
            while True:
                secs += 1
                print(f'   timer: {secs}', end='\r')
                sleep(1)
        except KeyboardInterrupt:
            return secs

    @staticmethod
    def convert_unix_to_datetime(total_time: int) -> Union[str, None]:
        """ Seconds from Unix epoch in date and time """
        if isinstance(total_time, int):
            dt: str = str(datetime.fromtimestamp(total_time))
            return dt
        return None


class SSL:
    """
    Check Support SSL certificate
    """
    @staticmethod
    def is_open_https_port(ip: str) -> bool:
        """ Check status HTTPS port Open or Close """
        cmd: list[str] = ['nmap', ip, '-p', '443']
        for string in sp.check_output(cmd).decode(encoding='utf-8').split('\n'):
            if 'open' in string:
                return True
        return False

    @staticmethod
    def exec_method(method: str) -> bool:
        """ Request via JSON_RPC """
        commad: list[str] = base_query() + ['-d', method, EndPoints.common]
        if not sp.run(commad, check=True).returncode:
            return True

        return False

    @staticmethod
    def start_generate_sslcert() -> None:
        """
        Wraps for run to a script
        that generates SSL certificates supported by the host
        """
        cwd: str = getcwd()
        script: str = 'generate_sslcert.sh'
        if script in sp.check_output(['ls', '-l', cwd]).decode(encoding='utf-8').split():
            command: list[str] = ['bash', f"{cwd}/{script}"]
            sp.run(command, check=True)
            return

        file_err = FileNotFoundError(f"File {script} not found in the current work dir !")
        raise file_err


# SNMP
@dataclass(frozen=False)
class BaseSNMPApi:
    """ Small API for working with SNMP """
    snmp_mode_on: str = '{"id":"1","method":"snmp.config.global.set","params":[{"Mode": true, "EngineId": "123456789B"}]}'
    get_info_engine_mode: str = '{"id":"1","method":"snmp.config.global.get","params":[]}'
    add_user: tuple = ('{"id":"1","method":"snmp.config.users.add","params":['\
                '{"EngineId": "123456789B", "UserName": "testuser"},'\
                '{"SecurityLevel": "snmpAuthPriv",'\
                '"AuthProtocol": "snmpMD5AuthProtocol",'\
                '"AuthPassword": "testpassword",'\
                '"PrivProtocol": "snmpDESPrivProtocol",'\
                '"PrivPassword": "testpassword"}]}',)
    get_users_config: str = '{"id":"1","method":"snmp.config.users.get","params":[{"EngineId": "123456789B", "UserName": "testuser"}]}'
    add_group: tuple = ('{"id":"1","method":"snmp.config.groups.add","params":['\
                        '{"SecurityModel": "usm", "UserOrCommunity": "testuser"}, {"AccessGroupName": "testgroup"}]}',)
    get_group_config: str = '{"id":"1","method":"snmp.config.groups.get","params":[{"SecurityModel": "usm", "UserOrCommunity": "testuser"}]}'
    add_snmp_access: tuple = ('{"id":"1","method":"snmp.config.accesses.add","params":['\
                            '{"AccessGroupName": "testgroup", "SecurityModel": "usm", "SecurityLevel": "snmpAuthPriv"},'\
                            '{"ReadViewName": "default_view", "WriteViewName": "default_view"}]}',)
    get_access_config: str = '{"id":"1","method":"snmp.config.accesses.get","params":[]}'

    @classmethod
    def __get_keys(cls) -> List[str]:
        """ Returns a list of keys """
        return [key for key in cls.__annotations__]

    @classmethod
    def __get_methods(cls) -> List[str]:
        """ Returns a list of methods """
        methods: List[str] = []
        for key in cls.__get_keys():
            method: str = cls.__dict__[key]
            if isinstance(method, tuple):
                # add string from tuple with index[0]
                method = cls.__dict__[key][0]
            methods.append(method)
        return methods

    @staticmethod
    def ret_val(obj: str) -> Union[List[str], None]:
        """
        Public interface
        return list[keys] | list[methods]
        """
        if obj == 'keys':
            return BaseSNMPApi.__get_keys()
        if obj == 'methods':
            return BaseSNMPApi.__get_methods()
        return None

@dataclass(frozen=False)
class SecondaryCall:
    """ Api only use SNMP test case """
    _read_field: str = '{"id":"1","method":"systemUtility.config.systemInfo.get","params":[]}'
    _snmp_mode_off: str = '{"id":"1","method":"snmp.config.global.set","params":[{"Mode": false, "EngineId": "123456789B"}]}'
    _get_info_engine_mode: str = '{"id":"1","method":"snmp.config.global.get","params":[]}'

    @classmethod
    def __get_methods(cls) -> List[str]:
        """ Not used in other modules"""
        return [
            cls._read_field,
            cls._snmp_mode_off,
            cls._get_info_engine_mode
        ]

    @staticmethod
    def ret_val(obj: str) -> Union[List[str], None]:
        """ Not used in other modules """
        if obj == 'methods':
            return SecondaryCall.__get_methods()
        return None
# End block SNMP
