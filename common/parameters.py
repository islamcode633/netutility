"""
Parameterization of dynamic structures
"""

from typing import List, Dict

PortIdentifier = str


class PoEParameters:
    """ Returns the data structures needed to execute a specific query """

    def poe_enable(self, flag: bool) -> List[bool]:
        """ Activate/Deactivate poe function """
        if isinstance(flag, bool):
            return [flag]
        raise TypeError('Error: flag must be of type: [ bool ]')

    def set_power_limit(self, current_power: int) -> List[str]:
        """ Set power limit """
        min_allowed_power: int = 30
        if current_power <= min_allowed_power:
            raise ValueError(f'Minimum allowable power: {min_allowed_power}W !')
        return [f'{current_power}']

    def set_port_state(self, port: PortIdentifier, state: str) -> List[PortIdentifier | Dict[str, str]]:
        """ Change state port [ Enabled | Disabled ] """
        state = state.lower()
        if state in {'enable', 'disable'}:
            return [f"Gi {port}", {"Mode": f"{state}"}]
        raise ValueError('Error: Ports state can be [ enable ] or [ disable ] !')

    def get_port_id(self, port: PortIdentifier) -> List[PortIdentifier]:
        """ Returns the port identifier """
        return [f"Gi {port}"]
