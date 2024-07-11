#!/usr/bin/env python3
""" Session Authentication module """
from datetime import datetime, timedelta
from api.v1.auth.session_exp_auth import SessionExpAuth
from models.user_session import UserSession


class SessionDBAuth(SessionExpAuth):
    """ Session DB Auth class
    """
    def create_session(self, user_id: str = None) -> str:
        """ Creates and stores new instance of UserSession
        """
        session_id = super().create_session(user_id)
        if not session_id:
            return None
        user_session = UserSession(user_id=user_id, session_id=session_id)
        user_session.save()
        return session_id

    def user_id_for_session_id(self, session_id=None) -> str:
        """ Returns User ID based on Session ID
        """
        if session_id is None:
            return None
        user_session = UserSession.search({'session_id': session_id})
        if not user_session:
            return None
        user_session = user_session[0]
        if self.session_duration <= 0:
            return user_session.user_id
        if (user_session.created_at) + \
                timedelta(seconds=self.session_duration) < datetime.now():
            return None
        return user_session.user_id
