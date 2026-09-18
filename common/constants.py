"""
Constants used in tests
"""

from typing import Final, List


# Successful completion of any request via JSON RPC
REQ_SUCCESS_CODE: Final[int] = 200
# Stop script execution for the specified number of seconds
PAUSE: Final[int] = 3

# --- using only PoE test
# Maximum power value(W)
POWER_LIMIT: Final[int] = 120
# Minimum allowable port voltage value
MINIMAL_POWER: Final[float] = 2.0
# Pause between data outputs after one successful test iteration
PAUSE_BETWEEN_OUT: Final[int] = 1
# ---
PASSED = 'PASSED'
FAILED = 'FAILED'

# setup
UTILS: Final[List[str]] = [
    'sshpass', 'bridge-utils', 'curl',
    'openssl', 'snmp', 'lldpd',
    'nmap', 'jq', ]
