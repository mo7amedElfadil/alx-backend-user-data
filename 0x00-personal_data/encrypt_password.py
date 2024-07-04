#!/usr/bin/env python3
""" Encrypt password using the bcrypt module
"""
from bcrypt import checkpw, hashpw, gensalt


def hash_password(password: str) -> bytes:
    """ Encrypts a password using bcrypt
    """
    return hashpw(password.encode(), gensalt())


def is_valid(hashed_password: bytes, password: str) -> bool:
    """ Check if the password is valid
    """
    return checkpw(password.encode(), hashed_password)
