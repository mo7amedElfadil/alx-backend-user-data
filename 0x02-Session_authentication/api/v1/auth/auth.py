#!/usr/bin/env python3
""" Authentication module """
from typing import List, TypeVar
from os import getenv


class Auth:
    """ Auth class
        Defines methods to authenticate a request
        Methods:
            - require_auth
            - authorization_header
            - current_user
    """

    def require_auth(self, path: str, excluded_paths: List[str]) -> bool:
        """ require auth method
            Args:
                path: string. Path to check
                excluded_paths: list of strings. Paths to exclude from auth
                    May end with * to match prefix
        """
        if not path or not excluded_paths:
            return True
        if path[-1] != '/':
            path += '/'
        for p in excluded_paths:
            if p[-1] == '*':
                if path.startswith(p[:-1]):
                    return False
            elif path == p:
                return False
        return True

    def authorization_header(self, request=None) -> str:
        """ authorization header method
            Tests if 'Authorization' is in the header of the request
        """
        if request is None:
            return None
        return request.headers.get('Authorization') or None

    def current_user(self, request=None) -> TypeVar('User'):
        """ current user method
            Overloaded in child class BasicAuth
        """
        return None

    def session_cookie(self, request=None):
        """ session cookie method
            Returns a cookie value from a request
        """
        if request is None:
            return None
        SESSION_NAME = getenv('SESSION_NAME')
        if not SESSION_NAME:
            return None
        return request.cookies.get(SESSION_NAME)
