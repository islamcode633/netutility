#!/usr/bin/env python3

"""
Client for testing a PoE chip
"""

import sys
from typing import List, Dict, Tuple, Any
from time import sleep

from jrpc_client import RpcRequest, get_client
from methods import PoEMethods
from parameters import PoEParameters
from constants import POWER_LIMIT, MINIMAL_POWER, PAUSE


class PoEEnableError(Exception):
    """ Error activating the poe function """

class ErrorSetPowerLimit(Exception):
    """ Error setting power limit """

class ErrorDisablePort(Exception):
    """ Failed to disable port ! """


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

def test_seq_activation_ports(
        ports: Tuple[str, ...],
        client: RpcRequest,
        method: PoEMethods,
        params: PoEParameters,
    ) -> Dict[str, str | int | bool]:
    """ Seq on/off PoE channels """
    names_failed_ports: str = ''
    success: int = 0
    failed: int = 0
    for port in ports:
        client.request(method.SET_CHANGE_PORT_STATE,
                        params.set_port_state(port=port, state='enable'))
        sleep(PAUSE)
        current_power: float = float(client.request(method.GET_INFO_PORT,
                                                    params.get_port_id(port=port))['Power'])
        if MINIMAL_POWER < current_power:
            success += 1
            print(f"<UI> {port}: {'%.1f'}W [ OK ]" % current_power)
            continue
        print(f"<UI> {port}: {'%.1f'}W [ Failed ]" % current_power)
        failed += 1
        names_failed_ports += port + " "
    return processing_result(failed, success, names_failed_ports)

def pre_config(
        ports: Tuple[str, ...],
        client: RpcRequest,
        method: PoEMethods,
        params: PoEParameters,
    ) -> None:
    """ Setup poe settings """
    try:
        is_poe_enable: Any = client.request(method.SET_POE_ENABLE, params.poe_enable(flag=True))
        if not is_poe_enable is None:
            raise PoEEnableError('Failed to activate PoE function !')
        is_set_power_limit: Any = client.request(method.SET_POWER_LIMIT,
                                                params.set_power_limit(current_power=POWER_LIMIT))
        if not is_set_power_limit is None:
            raise ErrorSetPowerLimit(f'Failed to set power to {POWER_LIMIT} !')
        # disable all ports
        for port in ports:
            is_disable_port: Any = client.request(method.SET_CHANGE_PORT_STATE,
                                                params.set_port_state(port=port, state='disable'))
            if is_disable_port is None:
                print(f'{port}: disable')
                continue
            raise ErrorDisablePort(f'Failed to disable port {port} !')
    except (PoEEnableError, ErrorSetPowerLimit, ErrorDisablePort) as e:
        sys.exit(f'{e}')


def get_poe_ports_id(result: List[Dict[str, str]]) -> Tuple[str, ...]:
    """ Ports on which PoE is enabled """
    return tuple(map.get('key', '').split()[1] for map in result)


if __name__ == '__main__':
    # point enter
    # init of objects required to run the test
    poe_client: RpcRequest = get_client()
    poe_method: PoEMethods = PoEMethods()
    poe_params: PoEParameters = PoEParameters()
    poe_ports: Tuple[str, ...] = get_poe_ports_id(poe_client.request(poe_method.GET_INFO_PORT))
    # setup stage
    pre_config(poe_ports, poe_client, poe_method, poe_params)
    # run test
    test: Dict[str, str | int | bool] = test_seq_activation_ports(poe_ports, poe_client, poe_method, poe_params)
    if test['result']:
        print('TEST OK ')
        sys.exit(0)
    print(f"TEST ERR: Port: {test['port']} Failed: {test['failed']}")
    sys.exit(1)
