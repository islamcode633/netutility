"""
Unit tests
"""

import sys
from typing import Optional

from parameters import PoEParameters
from methods import PoEMethods


class TestParams:
    """ Positive and Negative tests """
    _test_params: PoEParameters = PoEParameters()

    @classmethod
    def test_set_power_limit(cls) -> Optional[str]:
        """ ... """
        try:
            for v in [120, 35, 0]:
                print(f'{v}W: {int(cls._test_params.set_power_limit(current_power=v)[0]) == v}')
            return None
        except (TypeError, ValueError) as e:
            print(f'{v} - {e}')
            return '------'

    @classmethod
    def test_set_port_state(cls) -> Optional[str]:
        """ ... """
        try:
            for p, v in {'1/1':'enable', '1/2':'disable', '1/3':'en'}.items():
                print(cls._test_params.set_port_state(port=p, state=v))
            return None
        except (TypeError, ValueError) as e:
            print(f'port: {p} state: {v}  - {e}')
            return '------'

    @classmethod
    def test_poe_enable(cls) -> Optional[str]:
        """ ... """
        try:
            for v in [True, False, 1, 'True', 0]:
                print(isinstance(cls._test_params.poe_enable(flag=v)[0], bool))
            return None
        except TypeError as e:
            print(f'{v} - {e}')
            return '------'

def test_params() -> None:
    """ Check request parameters """
    print(TestParams.test_poe_enable())
    print(TestParams.test_set_port_state())
    print(TestParams.test_set_power_limit())

def test_methods() -> Optional[bool]:
    """ Check unintentional change of method """
    assert PoEMethods.GET_INFO_PORT == 'poe.port.status.get'
    assert PoEMethods.SET_POE_ENABLE == 'poe_enable.set'
    assert PoEMethods.SET_POWER_LIMIT == 'poe.power.limit.set'
    assert PoEMethods.SET_CHANGE_PORT_STATE == 'poe.port.enable.mode.set'
    return True


def main() -> None:
    """ Run tests """
    test_params()
    if test_methods():
        print('Unit test [PoEMethods] <-> Success')
        sys.exit(0)
    else:
        sys.exit('Unit test [PoEMethods] <-> Failed')

main()
