#!/usr/bin/env python3
""" DB module
"""
from typing import Dict
from sqlalchemy import create_engine
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from user import Base, User


class DB:
    """ DB class
    """

    def __init__(self) -> None:
        """ Initialize a new DB instance
        """
        self._engine = create_engine("sqlite:///a.db", echo=False)
        Base.metadata.drop_all(self._engine)
        Base.metadata.create_all(self._engine)
        self.__session = None

    @property
    def _session(self) -> Session:
        """ Memoized session object
        """
        if self.__session is None:
            DBSession = sessionmaker(bind=self._engine)
            self.__session = DBSession()
        return self.__session

    def add_user(self, email: str, hashed_password: str) -> User:
        """ Create user and add it to session

            Args:
                email (str): user email
                hashed_password (str): user password
            Returns:
                User object
        """

        user = User(email=email, hashed_password=hashed_password)
        self._session.add(user)
        self._session.commit()

        return user

    def _validate_attribs(self, kwargs: dict) -> None:
        """ Validate attributes in kwargs
            Args:
                kwargs (dict): key word arguments
            Raises:
                ValueError - when invalid keys are passed
       """
        columns = User.__table__.columns.keys()
        for key in kwargs.keys():
            if key not in columns:
                raise ValueError

    def find_user_by(self, **kwargs) -> User:
        """ Find user by key word arguments
            NoResultFound and InvalidRequestError are raised when
            - no results are found, or
            - wrong query arguments are passed,
            respectively.

            Args:
                **kwargs: key word arguments
            Raises:
                NoResultFound - when no results are found
                InvalidRequestError - when wrong query arguments are passed

            Returns:
                User object
        """
        try:
            self._validate_attribs(kwargs)
        except ValueError:
            raise InvalidRequestError

        user = self._session\
            .query(User)\
            .filter_by(**kwargs)\
            .one()

        if not user:
            raise NoResultFound

        return user

    def update_user(self, user_id: int, **kwargs: Dict[str, str]):
        """ Update user
            Args:
                user_id (int): user id
                **kwargs: key word arguments
            Raises:
                ValueError - when user_id is not found, or
                    attribute doesnt correspond to a column
            Returns:
                None
        """
        user = self.find_user_by(id=user_id)
        if not user:
            return
        self._validate_attribs(kwargs)
        for key, value in kwargs.items():
            setattr(user, key, value)

        self._session.commit()
