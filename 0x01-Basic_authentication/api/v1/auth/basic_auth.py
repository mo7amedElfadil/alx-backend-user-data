#!/usr/bin/env python3
""" Authentication module """
from base64 import b64decode
from api.v1.auth.auth import Auth
from models.user import User
from typing import TypeVar


class BasicAuth(Auth):
    """ BasicAuth class, Inherits from Auth
        Defines methods to authenticate a request with basic auth
        Methods:
            - extract_base64_authorization_header
            - decode_base64_authorization_header
            - extract_user_credentials
            - user_object_from_credentials
            - current_user
    """
    def extract_base64_authorization_header(self,
                                            authorization_header: str) -> str:
        """ Extract base64 authorization header
            Args:
                authorization_header: string. Authorization header
            Returns:
                string. Base64 authorization header
        """
        if authorization_header is None \
                or not isinstance(authorization_header, str) \
                or not authorization_header.startswith('Basic '):
            return None
        return authorization_header[6:]

    def decode_base64_authorization_header(self,
                                           base64_authorization_header: str
                                           ) -> str:
        """ Decode base64 authorization header
            Args:
                base64_authorization_header: string. Base64 authorization
                    header
            Returns:
                string. Decoded base64 authorization header
        """
        if base64_authorization_header is None \
                or not isinstance(base64_authorization_header,
                                  str):
            return None
        try:
            return b64decode(
                base64_authorization_header.encode('utf-8')).decode('utf-8')
        except Exception:
            return None

    def extract_user_credentials(self,
                                 decoded_base64_authorization_header: str
                                 ) -> (str, str):
        """ Extract user credentials
            Args:
                decoded_base64_authorization_header: string. Decoded base64
                authorization header
            Returns:
                tuple. User credentials
        """
        if decoded_base64_authorization_header is None \
                or not isinstance(decoded_base64_authorization_header, str) \
                or ':' not in decoded_base64_authorization_header:
            return (None, None)
        return tuple(decoded_base64_authorization_header.split(':', 1))

    def user_object_from_credentials(self,
                                     user_email: str,
                                     user_pwd: str
                                     ) -> TypeVar('User'):
        """ User object from credentials
            Args:
                user_email: string. User email
                user_pwd: string. User password
            Returns:
                User instance or None
        """
        if None in {user_email, user_pwd} \
                or any([not isinstance(i, str)
                        for i in {user_email, user_pwd}]):
            return None
        try:
            user = User.search({'email': user_email})
        except Exception:
            return None
        if not user:
            return None
        user = user[0]
        if not user.is_valid_password(user_pwd):
            return None
        return user

    def current_user(self, request=None) -> TypeVar('User'):
        """ Overloads auth.current_user and retrieves user instance
            Args:
                request: request object. Default is None
            Returns:
                User instance or None
        """
        auth_header = self.authorization_header(request)
        if not auth_header:
            return None
        base64_auth_header = self.extract_base64_authorization_header(
            auth_header)
        if not base64_auth_header:
            return None
        decoded_base64_auth_header = self.decode_base64_authorization_header(
            base64_auth_header)
        if not decoded_base64_auth_header:
            return None
        user_credentials = self.extract_user_credentials(
            decoded_base64_auth_header)
        if not all(user_credentials):
            return None
        return self.user_object_from_credentials(*user_credentials)
