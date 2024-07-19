#!/usr/bin/env python3
""" Authentication module """
from typing import Union
from uuid import uuid4

import bcrypt
from sqlalchemy.orm.exc import NoResultFound

from db import DB
from user import User


def _hash_password(password: str) -> str:
    """ Returns a salted, hashed password """
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


def _valid_password(password: str, hashed_password: str) -> bool:
    """ Check if password is valid """
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)


def _generate_uuid() -> str:
    """ Generate a new UUID """
    return str(uuid4())


class Auth:
    """Auth class to interact with the authentication database.
    """

    def __init__(self):
        """ Constructor for Auth class
        """
        self._db = DB()

    def register_user(self, email: str, password: str) -> User:
        """ Registers and hashes user password """
        try:
            self._db.find_user_by(email=email)
            raise ValueError(f"User {email} already exists")
        except NoResultFound:
            pass

        return self._db.add_user(email, _hash_password(password))

    def valid_login(self, email: str, password: str) -> bool:
        """ Check if password is valid """
        try:
            user = self._db.find_user_by(email=email)
            return _valid_password(password, user.hashed_password)
        except NoResultFound:
            return False

    def create_session(self, email: str) -> Union[str, None]:
        """ Create a new session """
        try:
            user = self._db.find_user_by(email=email)
            session_id = _generate_uuid()
            self._db.update_user(user.id, session_id=session_id)
        except NoResultFound:
            return None
        return session_id

    def get_user_from_session_id(self, session_id: str) -> User:
        """ Retrieves user object from session ID """
        if not session_id:
            return None
        try:
            return self._db.find_user_by(session_id=session_id)
        except NoResultFound:
            return None

    def destroy_session(self, user_id: int) -> None:
        """ Destroy a session """
        self._db.update_user(user_id, session_id=None)

    def get_reset_password_token(self, email: str) -> str:
        """ Generate a reset password token """
        try:
            user = self._db.find_user_by(email=email)
        except NoResultFound:
            raise ValueError
        self._db.update_user(user.id, reset_token=_generate_uuid())
        return user.reset_token

    def update_password(self, reset_token: str, password: str) -> None:
        """ Reset user's password """
        try:
            user = self._db.find_user_by(reset_token=reset_token)
        except NoResultFound:
            raise ValueError
        self._db.update_user(user.id,
                             hashed_password=_hash_password(password),
                             reset_token=None)
