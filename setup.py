#!/usr/bin/env python3

"""
Checking the Python version and platform.
Installing libraries.
"""

import sys
from subprocess import run, CalledProcessError


# only works with Python version 3.10 and above
if sys.version_info.major < 3 and sys.version_info.minor < 10:
    sys.exit('Install Python interpreter version 3.10 or higher !')

if not sys.platform.startswith('linux'):
    sys.exit('Test utility works only on the Linux platform !')

if __name__ == '__main__':
    try:
        cmd_install_external_libs = ['pip3', 'install', '-r', 'requirements.txt']
        run(cmd_install_external_libs, check=True)
    except CalledProcessError as e:
        sys.exit(f'{e}')
