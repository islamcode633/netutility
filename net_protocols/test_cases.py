"""
Collection of test cases
Controlling the flow of tests  execution
"""

import os
import sys
import subprocess as sp
from time import sleep
from typing import List, Optional

from data import RemoteConnection
from objects import (
    IPv,
    LLDP,
    SSHConnect,
    NetPorts,
    ResetButton,
    RTC,
    SSL,
    BaseSNMPApi,
    SecondaryCall,
    Temperature
)
from common.utils import (
    test_result,
    verify_id_vlan,
    check_for_remote_connection,
    exec_method,
    exec_methods,
    generate_cookie
)

from common.exceptions import (
    ConnectTimeOutError,
    RequiredVLANNotFoundError,
    HostNotAvailableError,
    CookieGenerateError,
    OpenHTTPSPortError,
    GenSSLCertError
)
from common.methods import TemperatureMethod
from common.jrpclib import get_client, RpcRequest

# STDOUT = sys.stdout.write


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


def lldp_ctl() -> Optional[str]:
    print('--- Start LLDP ---')
    sleep(3)
    client: Optional[str] = LLDP.get_lldp_from_client()
    switch: Optional[str] = LLDP.get_lldp_from_switch()

    if client and switch:
        return client + switch

    return None


def ssh_ctl() -> Optional[str]:
    print('--- Start SSH ---')
    sleep(3)
    with RemoteConnection(type_conn='telnet').init_conn_session() as tn_connect:
        raw: str = SSHConnect.get_info_about_ssh(tn_connect=tn_connect)
        reuslt: bool = SSHConnect.is_enabled(output=raw)
        if not reuslt:
            SSHConnect.activate(tn_connect=tn_connect)

    with RemoteConnection().init_conn_session() as ssh_connect:
        return verify_id_vlan(connect=ssh_connect, test_case='SSH')


def telnet_ctl() -> Optional[str]:
    print('--- Start Telnet ---')
    sleep(3)
    with RemoteConnection(type_conn='telnet').init_conn_session() as tn_connect:
        return verify_id_vlan(connect=tn_connect, test_case='Telnet')

    raise ConnectTimeOutError('Connection timed out !')


def net_ports_ctl() -> None:
    print('--- Start Disp Port Activity ---\n'
          'terminate the script [ CTRL + C ]\n')
    sleep(3)
    try:
        ipaddr: str = '192.168.127.253'
        if NetPorts.checking_switch_availability(host=ipaddr):
            while True:
                NetPorts.generate_icmp_packets(host=ipaddr)
        raise HostNotAvailableError('Host not available !')
    except KeyboardInterrupt:
        # Not Error
        print('\nKeyboard interruption of script execution !')


def dip_ctl() -> None:
    print('--- Start Dip-Switch ---')
    sleep(3)
    try:
        print(check_for_remote_connection())
        print(' 30s - OFF Dip-Switch')
        sleep(30)
        print('Trying to connect remotely ... ')
        check_for_remote_connection()
    except Exception:
        print('Expected error: TCP connection to device failed !')
        print(' 30s - ON Dip-Switch')
        sleep(30)
        remote_is_allowed = check_for_remote_connection().split()[-1]
        print(test_result('Dip-Switch', is_ok=remote_is_allowed == 'Allowed'))


def reset_ctl() -> None:
    print('--- Start Reset ---')
    sleep(3)
        # First init SSH session
    with RemoteConnection().init_conn_session() as ssh_conn:
        execute_commands = ResetButton.run_commands_context_conn_session(ssh_conn=ssh_conn)
        # Output default VLANs interface
        vlans: str = 'show vlan all'
        print(execute_commands(command=vlans))

        # Set vlan 10
        execute_commands(config_commands=[ 'vlan 10' ])
        # Check was added vlan 10
        if ResetButton.isadded_vlan(output=execute_commands(command=vlans)):
            print(execute_commands(command='copy running-config startup-config'))
        else:
            raise RequiredVLANNotFoundError('Failed to add VLAN 10 on switch !')

    ResetButton.do_reconnect(short_reset=True, wait_for_reconnect=120)
    with RemoteConnection().init_conn_session() as ssh_conn:
        # Re-init SSH session after Short reset
        execute_commands = ResetButton.run_commands_context_conn_session(ssh_conn=ssh_conn)
        print(execute_commands(command=vlans))

    ResetButton.do_reconnect(long_reset=True, wait_for_reconnect=150)
    with RemoteConnection().init_conn_session() as ssh_conn:
        # Re-init SSH session after Long reset
        execute_commands = ResetButton.run_commands_context_conn_session(ssh_conn=ssh_conn)
        print(output := execute_commands(command=vlans),
              test_result(name='Reset', is_ok=not ResetButton.isadded_vlan(output)))


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


def syslog_ctl() -> None:
    print('--- Start Syslog ---')
    sleep(3)
    try:
        generate_cookie()
        def syslog() -> bool:
            """ ... """
            methods: dict[str, str] = {
                'clear_history': '{"id":"1","method":"syslog.control.history.set","params":[1, "all", {"Clear": true}]}',
                'get_current_history': '{"id":"1","method":"syslog.status.history.get","params":[]}',
                'get_current_interface': '{"id":"1","method":"ip.config.interface.get","params":[]}',
                'add_interface': '{"id":"1","method":"ip.config.interface.add","params":["VLAN 2"]}',
                'get_after_edit_interface': '{"id":"1","method":"ip.config.interface.get","params":[]}',
                'get_after_edit_history': '{"id":"1","method":"syslog.status.history.get","params":[]}',
            }
            for operation, method in methods.items():
                print(f"{operation.replace('_', ' ')}: ",
                      exec_method(
                          method=method,
                          operation=operation), end='')
                sleep(1)
            return True
        print(test_result('Syslog', is_ok=syslog()))
    except (CookieGenerateError, sp.CalledProcessError) as e:
        print(e)
        sys.exit(1)


def ssl_ctl() -> None:
    print('--- Start SSL ---')
    sleep(3)
    methods: dict[str, str] = {
        'generate_ssl': '{"id":"1","method":"https.config.certGenerate.set","params":["Gererate": true]}',
        'active_https_mode': '{"id":"1","method":"https.config.global.set","params":[{"Mode": true, "RedirectToHttps": false}]}',
    }
    try:
        generate_cookie()
        if SSL.exec_method(method=methods['generate_ssl']):
            print('Generated SSL certificates')
        else:
            raise GenSSLCertError('Error generating SSL certificates !')

        if SSL.is_open_https_port(ip=RemoteConnection().ipv4_switch):
            pass
        else:
            if SSL.exec_method(method=methods['active_https_mode']):
                print('HTTPS port: Open')
            else:
                raise OpenHTTPSPortError('Failed to open HTTPS port !')
        print(test_result('SSL', is_ok=SSL.start_generate_sslcert()))
    except (GenSSLCertError, OpenHTTPSPortError, FileNotFoundError) as e:
        print(e)
        sys.exit(1)


def snmp_ctl() -> None:
    print('--- Start SNMP ---')
    sleep(3)
    try:
        generate_cookie()
        script: List[str] = ['bash', f"{os.getcwd()}/scripts/snmp.sh"]
        if exec_methods(methods=BaseSNMPApi.ret_val(obj='methods')):
            sp.run(script, check=True)
            print(test_result('SNMP', \
                              is_ok=exec_methods(methods=SecondaryCall.ret_val(obj='methods'))))
    except Exception as e:
        sys.exit(f"{e}")


def temp_ctl() -> None:
    """ Test Case: Checking Temperature """
    client: RpcRequest = get_client()
    methods: TemperatureMethod = TemperatureMethod()
    cpu, phy1, phy2 = client.request(methods.GET_LATEST_CHANGES_SENSOR)
    try:
        temp_cpu: float = cpu['val']['Temp']
        temp_phy1: float = phy1['val']['Temp']
        temp_phy2: float = phy2['val']['Temp']
        if Temperature.is_cpu_ok(temp_cpu) \
            and Temperature.is_phy_ok(temp_phy1) \
            and Temperature.is_phy_ok(temp_phy2):
            print(f'CPU:  {temp_cpu} °C \nPHY1: {temp_phy1} °C \nPHY2: {temp_phy2} °C')
            test_result('Temperature', is_ok=True)
            return
        test_result('Temperature', is_ok=False)
    except KeyError:
        sys.exit('Error: keys <val> or <Temp> not found !')
