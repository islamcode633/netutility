"""
Collection of test cases
Controlling the flow of tests  execution
"""

import os
import sys
import subprocess as sp
from time import sleep
from typing import (
    List,
    Dict,
    Union,
    Any
)
from json import loads

from objects import (
    RemoteConnection,
    IPv,
    LLDP,
    SSHConnect,
    NetPorts,
    ResetButton,
    RTC,
    SSL,
    # SNMP
    BaseSNMPApi,
    SecondaryCall,
)
from auth_and_basequery_via_api import (
    generate_cookie,
    base_query,
    EndPoints
)
from exceptions import (
    ConnectTimeOut,
    RequiredVLANNotFound,
    HostNotAvailable,
    CookieGenerateError,
    FailedOpenHTTPSPort,
    ErrorGeneratingSSLCertificates
)


def ipv4_6_ctl() -> None:
    print('--- Start IPv4/6 ---')
    sleep(3)
    with RemoteConnection().init_conn_session() as ssh_session:
        nm800 = RemoteConnection()
        clear_ip_stat, show_ip_stat, ping = IPv.check_ip_protocol_version(host=nm800.ipv4_switch)
        IPv.clear_ip_statistics(command=clear_ip_stat, ssh_session=ssh_session)
        IPv.output_ip_statistics(command=show_ip_stat, ssh_session=ssh_session)
        IPv.icmp_request(command=ping)
        IPv.output_ip_statistics(command=show_ip_stat, ssh_session=ssh_session)


def lldp_ctl() -> Union[str, None]:
    print('--- Start LLDP ---')
    sleep(3)
    client: Union[str, None] = LLDP.get_lldp_from_client()
    switch: Union[str, None] = LLDP.get_lldp_from_switch()

    if client and switch:
        return client + switch

    return None


def verify_id_vlan(connect, test_case: str = "") -> Union[str, None]:
    """ Checking the existence of VLAN with ID 1 """
    if not test_case:
        return None

    output: List[str] = str(connect.send_command('show vlan id 1')).split()
    if output.index('1'):
        return f'--- {test_case}: PASSED'


def ssh_ctl() -> Union[str, None]:
    print('--- Start SSH ---')
    sleep(3)
    with RemoteConnection(type_conn='telnet').init_conn_session() as tn_connect:
        raw: str = SSHConnect.get_info_about_ssh(tn_connect=tn_connect)
        reuslt: bool = SSHConnect.is_enabled(output=raw)
        if not reuslt:
            SSHConnect.activate(tn_connect=tn_connect)

    with RemoteConnection().init_conn_session() as ssh_connect:
        return verify_id_vlan(connect=ssh_connect, test_case='SSH')


def telnet_ctl() -> Union[str, None]:
    print('--- Start Telnet ---')
    sleep(3)
    with RemoteConnection(type_conn='telnet').init_conn_session() as tn_connect:
        return verify_id_vlan(connect=tn_connect, test_case='Telnet')

    raise ConnectTimeOut('Connection timed out !')


def net_ports_ctl() -> None:
    print('--- Start DispPortActivity ---\n' \
        'terminate the script [ CTRL + C ]\n')
    sleep(3)
    try:
        ipaddr: str = '192.168.127.253'
        if NetPorts.checking_switch_availability(host=ipaddr):
            while True:
                NetPorts.generate_icmp_packets(host=ipaddr)
        raise HostNotAvailable('Host not available !')
    except KeyboardInterrupt:
        # Not Error
        print('\nKeyboard interruption of script execution !')


def check_for_remote_connection() -> (str | List[Any] | Dict[str, Any]):
    """ Checking remote access via ssh """
    ssh_conn: Any = RemoteConnection().init_conn_session()
    return ssh_conn.send_command('show dipinfo functional')

def dip_ctl() -> None:
    print('--- Start Dip-Switch ---')
    sleep(3)
    try:
        print(check_for_remote_connection())
        print(' 30s - OFF Dip-Switch - ')
        sleep(30)
        print('Trying to connect remotely ... ')
        check_for_remote_connection()
    except Exception:
        print('Error: Connect time out !')
        print(' 30s - ON Dip-Switch - ')
        sleep(30)
        print(check_for_remote_connection())


def reset_ctl() -> None:
    print('--- Start Reset ---')
    sleep(3)
        # First init SSH session
    with RemoteConnection().init_conn_session() as ssh_conn:
        execute_commands = ResetButton.run_commands_context_conn_session(ssh_conn=ssh_conn)
        # Output default VLANs interface
        vlans: str = 'show vlan all'
        print(execute_commands(command=vlans))

        config_commands: List[str] = [
                'vlan 10',
                'interface GigabitEthernet 1/1',
                'switchport mode access',
                'switchport access vlan 10'
            ]
        # Set vlan 10
        execute_commands(config_commands=config_commands)
        # Check was added vlan 10
        if ResetButton.isadded_vlan(output=execute_commands(command=vlans)):
            print(execute_commands(command='copy running-config startup-config'))
        else:
            raise RequiredVLANNotFound('Failed to add VLAN 10 on switch !')

    ResetButton.do_reconnect(short_reset=True, wait_for_reconnect=120)
    with RemoteConnection().init_conn_session() as ssh_conn:
        # Re-init SSH session after Short reset
        execute_commands = ResetButton.run_commands_context_conn_session(ssh_conn=ssh_conn)
        print(execute_commands(command=vlans))

    ResetButton.do_reconnect(long_reset=True, wait_for_reconnect=150)
    with RemoteConnection().init_conn_session() as ssh_conn:
        # Re-init SSH session after Long reset
        execute_commands = ResetButton.run_commands_context_conn_session(ssh_conn=ssh_conn)
        print(execute_commands(command=vlans))


def rtc_ctl() -> None:
    print('--- Start RTC ---')
    sleep(3)
    with RemoteConnection().init_conn_session() as ssh_conn:
        default_datetime: str = RTC.configure_datetime(ssh_conn=ssh_conn, flag='set_dt')

    seconds: int = RTC.convert_datetime_to_unix(dt=default_datetime)
    timer: int = RTC.counter_time()
    # constant 6 approximately the time spent on an SSH Session
    total_time: int = timer + seconds + 6

    print(f'\nSet time:     {default_datetime}')
    print(f'Expected time: {RTC.convert_unix_to_datetime(total_time=total_time)} deviation by +-[2:3] sec')
    with RemoteConnection().init_conn_session() as ssh_conn:
        print(f'Current time: {RTC.configure_datetime(ssh_conn=ssh_conn)}')


def exec_method(method: str = '', operation: str = '') -> bytes:
    """ Сommon method for all requests """
    mapping_operations_on_the_answer_set: dict[str, str] = {
        'clear_history': '.error',
        'get_current_history': '.result',
        'get_current_interface': '.result|from_entries|has("VLAN 2")',
        'add_interface': '.error',
        'get_after_edit_interface': '.result|from_entries|has("VLAN 2")',
        'get_after_edit_history': '.result[0].val.MsgText'
    }
    command: list[str] = base_query() + ['-d', method, EndPoints.common ]
    with sp.Popen(command, stdout=sp.PIPE) as proc:
        output: bytes = sp.check_output((
                    'jq',
                    mapping_operations_on_the_answer_set[operation]
                    ),
                    stdin=proc.stdout
                )
    return output

def syslog_ctl() -> None:
    print('--- Start Syslog ---')
    sleep(3)
    try:
        generate_cookie()

        methods: dict[str, str] = {
            'clear_history': '{"id":"1","method":"syslog.control.history.set","params":[1, "all", {"Clear": true}]}',
            'get_current_history': '{"id":"1","method":"syslog.status.history.get","params":[]}',
            'get_current_interface': '{"id":"1","method":"ip.config.interface.get","params":[]}',
            'add_interface': '{"id":"1","method":"ip.config.interface.add","params":["VLAN 2"]}',
            'get_after_edit_interface': '{"id":"1","method":"ip.config.interface.get","params":[]}',
            'get_after_edit_history': '{"id":"1","method":"syslog.status.history.get","params":[]}',
        }

        for operation, method in methods.items():
            print(f"{operation}: ", \
                    exec_method(
                        method=method,
                        operation=operation
                    ).decode('utf-8'))
            sleep(3)
    except CookieGenerateError as e:
        print(e)
    except sp.CalledProcessError as e:
        print(e)


def ssl_ctl() -> None:
    print('--- Start SSL ---')
    sleep(3)
    methods: dict[str, str] = {
        'generate_ssl': '{"id":"1","method":"https.config.certGenerate.set","params":["Gererate": true]}',
        'active_https_mode': '{"id":"1","method":"https.config.global.set","params":[{"Mode": true, "RedirectToHttps": false}]}',
    }
    try:
        generate_cookie()
        sleep(2)

        if SSL.exec_method(method=methods['generate_ssl']):
            print('Generated SSL certificates\n')
            sleep(2)
        else:
            raise ErrorGeneratingSSLCertificates('Error generating SSL certificates !')

        if SSL.is_open_https_port(ip=RemoteConnection().ipv4_switch):
            pass
        else:
            if SSL.exec_method(method=methods['active_https_mode']):
                print('\nHTTPS port: Open')
                sleep(2)
            else:
                raise FailedOpenHTTPSPort('Failed to open HTTPS port !')
        SSL.start_generate_sslcert()
    except Exception as e:
        print(e)
        sys.exit()

# SNMP
def parse(output: Any) -> None:
    """ Host data analysis """
    if not output:
        pass
    else:
        try:
            _ = [print(f"{key}: {output[key]}") for _, key in enumerate(output)]
        except Exception:
            _ = [print(f"{key}: {output[0]['key'][key]}") for key in output[0]['key']]


def exec_methods(methods: Any) -> bool:
    """ Synchronous API call """
    for method in methods:
        command: List[str] = base_query() + ['-d', method, EndPoints.common]
        with sp.Popen(command, stdout=sp.PIPE) as proc:
            parse(output=loads(sp.check_output(('jq', '.result'), stdin=proc.stdout)))
        sleep(3)
    return True


def snmp_ctl() -> None:
    print('--- Start SNMP ---')
    sleep(3)
    try:
        generate_cookie()
        command: List[str] = ['bash', f"{os.getcwd()}/snmp.sh"]
        if exec_methods(methods=BaseSNMPApi.ret_val(obj='methods')):
            sp.run(command, check=True)
            if exec_methods(methods=SecondaryCall.ret_val(obj='methods')):
                print('\nSNMP: PASSED')
    except Exception as e:
        print(e)
        sys.exit()
# End block SNMP
