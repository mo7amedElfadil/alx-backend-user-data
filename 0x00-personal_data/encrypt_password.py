#!/usr/bin/env python3
""" Encrypt password using the bcrypt module
"""
import bcrypt


def hash_password(password: str) -> bytes:
    """ Encrypts a password using bcrypt
        Args:
            password: a string to be encrypted
        Returns:
            a bytes object containing the encrypted password
    """
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())


def is_valid(hashed_password: bytes, password: str) -> bool:
    """ Check if the password is valid
        Args:
            hashed_password: a bytes object containing the encrypted password
            password: a string to be checked
        Returns:
            a boolean value indicating if the password is valid
    """
    return bcrypt.checkpw(password.encode(), hashed_password)
