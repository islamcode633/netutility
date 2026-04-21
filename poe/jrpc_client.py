"""
Library for sending requests via json-rpc v1.0
"""

import sys
from typing import Dict, Any
from requests import Session, Response

from constants import REQ_SUCCESS_CODE


class AuthError(Exception):
    """ Failed to log in """

class ParameterNotFoundError(Exception):
    """ Error initializing required parameters """

class ServerResponseError(Exception):
    """ Base class of errors in server response """


class RpcRequest:
    """ Creates an object that represents a single public API for all RPC requests """
    def __init__(self, session: Session) -> None:
        self._session = session
        self._json_rpc_url: str = 'http://192.168.127.253/json_rpc'

    def _post(self, payload: Dict[str, Any]) -> Any:
        """ Wrapper for sending a POST request """
        response: Response = self._session.post(url=self._json_rpc_url, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()

    def request(self, method: str = "", params: Any | None = None) -> Any:
        """ Public api for post queries """
        if not method:
            raise ParameterNotFoundError('Param: [ method ] not init valid value !')
        payload: Dict[str, Any] = {
            "id": "1",
            "method": f"{method}",
            "params": params or []
        }
        response: Dict[str, Any] = self._post(payload=payload)
        if response['error'] is None:
            return response['result']
        raise ServerResponseError(f"{response['error']}")

def _create_session(
        session: Session = Session(),
        loggin_url: str = 'http://192.168.127.253/login',
        user: str = 'admin:password'
    ) -> Session:
    """ returns a Session object """
    res_code: int = session.post(
        url=loggin_url,
        data=user
    ).status_code
    if res_code == REQ_SUCCESS_CODE:
        # Session object with Cookie field after success auth
        return session
    raise AuthError('Authorization error on the switch !')

def get_client() -> RpcRequest:
    """ return Client to perform RPC requests """
    try:
        return RpcRequest(session=_create_session())
    except (AuthError, ParameterNotFoundError, RecursionError) as e:
        sys.exit(f'{e}')
