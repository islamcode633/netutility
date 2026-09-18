"""
Specific Test Case errors
"""

# net_protocols
class CommandNotFoundError(Exception):
    """
    Сommand was not passed to the function
    for remote execution on the switch
    """

class RequiredVLANNotFoundError(Exception):
    """ Failed to add VLAN 10 on switch """


class ResetModeNotSelectedError(Exception):
    """ One of the reset modes is not selected """


class ShortPeriodOfTimeToConnectError(Exception):
    """ Required time to connect 120 seconds or more """


class HostNotAvailableError(Exception):
    """ Host not available """


class ConnectTimeOutError(Exception):
    """ Connection timed out """


class CookieGenerateError(Exception):
    """ Failed to generate cookies """


class OpenHTTPSPortError(Exception):
    """ Failed to open https port """


class GenSSLCertError(Exception):
    """ Error generating SSL certificates """


# jrpclib
class AuthError(Exception):
    """ Failed to log in """

class ParameterNotFoundError(Exception):
    """ Error initializing required parameters """

class ServerResponseError(Exception):
    """ Base class of errors in server response """

# PoE
class PoEEnableError(Exception):
    """ Error activating the poe function """

class SetPowerLimitError(Exception):
    """ Error setting power limit """

class DisablePortError(Exception):
    """ Failed to disable port ! """

# setup
class PyVersionError(Exception):
    """ Python interpreter version mismatch """

class PlatformError(Exception):
    """ Expected OS platform error """
