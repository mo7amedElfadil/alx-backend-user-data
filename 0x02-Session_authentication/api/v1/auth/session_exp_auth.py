#!/usr/bin/env python3
""" Session Authentication module """
from os import getenv
from datetime import datetime, timedelta
from api.v1.auth.session_auth import SessionAuth


class SessionExpAuth(SessionAuth):
    """ Session Exp Auth class """
    def __init__(self):
        """ Constructor
            Set the session duration in the environment variable
        """
        try:
            self.session_duration = int(getenv('SESSION_DURATION', 0))
        except ValueError:
            self.session_duration = 0

    def create_session(self, user_id: str = None) -> str:
        """ Creates a Session ID for a user_id
            Sets the session dictionary based on the session ID with
            user ID and created_at key/value pairs
        """
        session_id = super().create_session(user_id)
        if not session_id:
            return None

        self.user_id_by_session_id[session_id] = {
            'user_id': user_id,
            'created_at': datetime.now()
        }
        return session_id

    def user_id_for_session_id(self, session_id: str = None) -> str:
        """ returns a User ID based on a Session ID
            Determines if session time is expired
        """
        if not session_id:
            return None

        session_dictionary = self.user_id_by_session_id.get(session_id)
        if not session_dictionary:
            return None

        if self.session_duration <= 0:
            return session_dictionary.get('user_id')

        if 'created_at' not in session_dictionary:
            return None

        if (session_dictionary.get('created_at')) + \
                timedelta(seconds=self.session_duration) < datetime.now():
            return None

        return session_dictionary.get('user_id')
