"""
Auxiliary functions
"""

import sys
import subprocess as sp
from typing import (
    List,
    Dict,
    Tuple,
    Optional,
    Any
)
from dataclasses import dataclass
from json import loads

from common.constants import POWER_LIMIT, PASSED, FAILED
from common.exceptions import (
    CookieGenerateError,
    PoEEnableError,
    SetPowerLimitError,
    DisablePortError
)
from net_protocols.data import RemoteConnection


@dataclass(frozen=True)
class EndPoints:
    """ 
    Contains API.

    :common: api for all calls
    :login: api only for auth
    """
    common: str = 'http://192.168.127.253/json_rpc'
    login: str = 'http://192.168.127.253/login'

@dataclass(frozen=True)
class User:
    """ Init User """
    username: str = 'admin'
    password: str = 'password'

@dataclass(frozen=True)
class DataQuery:
    """
    Data for the request.
 
    :header: JSON
    :path_to_cookie: generated cookie
    """
    header: str = '-H Content-Type: application/json'
    path_to_cookie: str = '/tmp/auth.cookie'

def generate_cookie() -> None:
    """ Creating a cookie file at the specified path """
    command: list[str] = f"curl -c {DataQuery.path_to_cookie} \
        -d {User.username}:{User.password} {EndPoints.login}".split()
    if not sp.run(command, check=True).check_returncode():
        return None
    raise CookieGenerateError('Failed to Generate Cookies !')

def base_query() -> list[str]:
    """ Return basic command in every request """
    return ['curl', '-s', '-b', f"{DataQuery.path_to_cookie}", f"{DataQuery.header}",]


def test_result(name: str, is_ok: bool) -> str:
    """ Returns the result of the passed/failed test """
    return f"--- {name}: {PASSED if is_ok else FAILED} ---\n"


# net_protocols
def verify_id_vlan(connect, test_case: str = "") -> Optional[str]:
    """ Checking the existence of VLAN with ID 1 """
    if not test_case:
        return None

    output: List[str] = str(connect.send_command('show vlan id 1')).split()
    if output.index('1'):
        return test_result(name=test_case, is_ok=True)

def check_for_remote_connection() -> str:
    """ Checking remote access via ssh """
    ssh_conn: Any = RemoteConnection().init_conn_session()
    return ssh_conn.send_command('show dipinfo functional')

def _parse(output: Any) -> None:
    """ Host data analysis """
    if not output:
        pass
    else:
        try:
            for _, key in enumerate(output):
                print(f"{key}: {output[key]}")
        except Exception:
            for key in output[0]['key']:
                print(f"{key}: {output[0]['key'][key]}")

def exec_methods(methods: Any) -> bool:
    """ Synchronous API call """
    base_cmd: list[str] = base_query()
    for method in methods:
        command: List[str] = base_cmd + ['-d', method, EndPoints.common]
        with sp.Popen(command, stdout=sp.PIPE) as proc:
            _parse(output=loads(sp.check_output(('jq', '.result'), stdin=proc.stdout)))
    return True

def exec_method(method: str = '', operation: str = '') -> str:
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
        output: bytes = sp.check_output(('jq',
                                         mapping_operations_on_the_answer_set[operation]),
                                         stdin=proc.stdout)

    return output.decode('utf-8')
# end

# POE
def _errors_counting(ports: List[str]) -> str:
    """ Counts the number of errors for each port """
    res: str = ""
    for uport in sorted(set(ports)):
        frequent: int = 0
        for port in ports:
            if uport == port:
                frequent += 1
        res += f'{uport[-1]}({frequent}) '
    return res

def processing_result(
        failed: int,
        success: int,
        names_failed_ports: str
    )-> Dict[str, str | int | bool]:
    """ Test data processing """
    result: Dict[str, str | int | bool] = {
        'success': success, 'failed': failed,
        'port': "", 'result': True
    }
    if failed:
        result.update({'result': False})
        result.update({'port': _errors_counting(names_failed_ports.strip().split())})
    return result

def get_poe_ports_id(result: List[Dict[str, str]]) -> Tuple[str, ...]:
    """ Ports on which PoE is enabled """
    return tuple(map.get('key', '').split()[1] for map in result)

def pre_config(ports: Tuple[str, ...], client, method, params) -> None:
    """ Setup poe settings """
    try:
        is_poe_enable: Any = client.request(method.SET_POE_ENABLE, params.poe_enable(flag=True))
        if not is_poe_enable is None:
            raise PoEEnableError('Failed to activate PoE function !')
        is_set_power_limit: Any = client.request(method.SET_POWER_LIMIT,
                                                params.set_power_limit(current_power=POWER_LIMIT))
        if not is_set_power_limit is None:
            raise SetPowerLimitError(f'Failed to set power to {POWER_LIMIT} !')
        # disable all ports
        for port in ports:
            is_disable_port: Any = client.request(method.SET_CHANGE_PORT_STATE,
                                                params.set_port_state(port=port, state='disable'))
            if is_disable_port is None:
                print(f'{port}: disable')
                continue
            raise DisablePortError(f'Failed to disable port {port} !')
    except (PoEEnableError, SetPowerLimitError, DisablePortError) as e:
        sys.exit(f'{e}')
# end
