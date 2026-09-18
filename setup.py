#!/usr/bin/env python3

"""
Checking the Python version and platform.
Installing libraries and extern utils.
"""

import sys
import subprocess as sp

from common.constants import UTILS
from common.exceptions import PyVersionError, PlatformError


class Check:
    """ General check """
    @classmethod
    def is_expected_pyvers(cls) -> bool:
        """ Checking for the required Python interpreter version """
        if sys.version_info.major == 3 and sys.version_info.minor >= 10:
            return True
        raise PyVersionError("Install Python interpreter version 3.10 or higher !")

    @classmethod
    def is_linux_platform(cls) -> bool:
        """ Verification of the test utility launch on the Linux platform """
        if sys.platform.startswith('linux'):
            return True
        raise PlatformError("Test utility works only on the Linux platform !")

class ProjectSetting:
    """ An abstraction describing the project configuration process """
    @classmethod
    def update_of_available_pckgs(cls) -> None:
        """ Indexing an APT remote repository packages """
        sp.run('sudo apt update'.split(), check=True)

    @classmethod
    def install_of_must_have_pckgs(cls) -> None:
        """ Installation of the necessary packages (utilities) for running tests """
        sp.run('sudo apt install -y'.split() + UTILS, check=True)

    @classmethod
    def install_pylibs(cls) -> None:
        """ Installing external Python libraries """
        sp.run('pip3 install -r requirements.txt'.split(), check=True)


if __name__ == '__main__':
    try:
        if Check.is_expected_pyvers() and Check.is_linux_platform():
            ProjectSetting.update_of_available_pckgs()
            ProjectSetting.install_of_must_have_pckgs()
            ProjectSetting.install_pylibs()
    except (PyVersionError, PlatformError) as e:
        print(e)
        sys.exit(1)
