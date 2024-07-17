#!/usr/bin/env python3
""" User class module """
from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class User(Base):
    """ User class
        Args:
            Base (declarative_base): Base class
        Attributes:
            __tablename__ (str): table name
            id (int, primary_key): user id
            email (str, Not Null): user email
            hashed_password (str, Not Null): user password
            session_id (str): user session id
            reset_token (str): user reset token
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String(250), nullable=False)
    hashed_password = Column(String(250), nullable=False)
    session_id = Column(String(250))
    reset_token = Column(String(250))
