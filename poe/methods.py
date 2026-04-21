"""
Contains the methods needed to perform Get/Set requests
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class PoEMethods:
    """
    :GET_INFO_PORT: get general information about ports
                    (voltage, PoE port ID, etc.)
    :SET_POE_ENABLE: activates the PoE function
    :SET_POWER_LIMIT: maximum power setting
    :SET_CHANGE_PORT_STATE: for changing the on/off state of a port
    """
    GET_POWER_TOTAL       = "poe.power.total.get"
    GET_POWER_PARAMETERS  = "poe.power.parameters.get"
    GET_POWER_LIMIT       = "poe.power.limit.get"
    GET_DEVICE_STATUS     = "poe.device.status.get"
    GET_PORT_PARAMS       = "poe.port.parameters.get"
    GET_ERROR_COUNTERS    = "poe.port.counters.get"
    GET_PORT_CLASS        = "poe.port.class.get"
    GET_POE_VERSION       = "poe.version.get"
    GET_INFO_CLASS_POWER  = "poe.power.class.info.get"
    GET_PORT_MEASUREMENTS = "poe.port.measurements.get"
    # Gi {port} -> resp['result']['Power']
    GET_INFO_PORT         = "poe.port.status.get"

    SET_POE_ENABLE        = "poe_enable.set"
    SET_POWER_LIMIT       = "poe.power.limit.set"
    # Gi {port} , {"Mode": "enabled"}
    SET_CHANGE_PORT_STATE = "poe.port.enable.mode.set"
