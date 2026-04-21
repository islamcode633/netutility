"""
The module provides:
    1) Authorization data
    2) Basic request (curl) which is the basis for all requests
    3) Endpoints
"""

import subprocess as sp
from dataclasses import dataclass

from exceptions import CookieGenerateError


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
    command: list[str] = f"curl -c {DataQuery.path_to_cookie} -d {User.username}:{User.password} {EndPoints.login}".split()
    if not sp.run(command, check=True).check_returncode():
        print('Cookies Generated\n')
        return

    raise CookieGenerateError('Failed to Generate Cookies !')


def base_query() -> list[str]:
    """ Return basic command in every request """
    return ['curl', '-s', '-b', f"{DataQuery.path_to_cookie}", f"{DataQuery.header}",]
