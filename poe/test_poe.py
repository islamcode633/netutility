#!/usr/bin/env python3

"""
Client for testing a PoE chip
"""

import sys
from typing import Dict, Tuple
from time import sleep

from common.utils import processing_result, get_poe_ports_id, pre_config #test_result
from common.methods import PoEMethods
from common.parameters import PoEParameters
from common.constants import MINIMAL_POWER, PAUSE
from common.jrpclib import RpcRequest, get_client


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


def poe_ctl():
    """ ... """
    # init of objects required to run the test
    poe_client: RpcRequest = get_client()
    poe_method: PoEMethods = PoEMethods()
    poe_params: PoEParameters = PoEParameters()
    poe_ports: Tuple[str, ...] = get_poe_ports_id(poe_client.request(poe_method.GET_INFO_PORT))
    # setup stage
    pre_config(poe_ports, poe_client, poe_method, poe_params)
    # run test
    test: Dict[str, str | int | bool] = test_seq_activation_ports(poe_ports, poe_client, poe_method, poe_params)
    # test_result()
    if test['result']:
        print('TEST OK ')
        sys.exit(0)
    print(f"TEST ERR: Port: {test['port']} Failed: {test['failed']}")
    sys.exit(1)
