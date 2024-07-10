#!/usr/bin/env python3
""" Session Authentication module """
from base64 import b64decode
from api.v1.auth.auth import Auth
from models.user import User
from typing import TypeVar
from uuid import uuid4


class SessionAuth(Auth):
    """ Session Authentication class """
    user_id_by_session_id = {}

    def create_session(self, user_id: str = None) -> str:
        """ Creates a Session ID for a user_id """
        if user_id is None \
                or not isinstance(user_id, str):
            return None
        session_id = str(uuid4())
        self.user_id_by_session_id[session_id] = user_id
        return session_id

    def user_id_for_session_id(self, session_id: str = None) -> str:
        """  returns a User ID based on a Session ID
        """
        if not session_id \
                or not isinstance(session_id, str):
            return None
        return self.user_id_by_session_id.get(session_id)

    def current_user(self, request=None):
        """ returns a User instance based on a cookie value """

        return User.get(
                self.user_id_for_session_id(
                    self.session_cookie(
                        request)))
