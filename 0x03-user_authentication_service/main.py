#!/usr/bin/env python3
import requests

API_URL = "http://localhost:5000"
EMAIL = "guillaume@holberton.io"
PASSWD = "b4l0u"
NEW_PASSWD = "t4rt1fl3tt3"


def register_user(email: str, password: str) -> None:
    """ Register a user
        Testing for the users post route
        Args:
            email: email of the user
            password: password of the user
    """
    url = f"{API_URL}/users"
    data = {
        "email": email,
        "password": password
    }
    response = requests.post(url, data=data)
    assert response.status_code == 200
    assert response.json() == {"email": email, "message": "user created"}

    # register the user again
    response = requests.post(url, data=data)
    assert response.status_code == 400
    assert response.json() == {"message": "email already registered"}


def log_in_wrong_password(email: str, password: str) -> None:
    """ Log in with wrong password
        Args:
            email: email of the user
            password: password of the user
    """
    url = f"{API_URL}/sessions"
    data = {
        "email": email,
        "password": password
    }
    response = requests.post(url, data=data)
    assert response.status_code == 401


def log_in(email: str, password: str) -> str:
    """ Log in with right password
        Args:
            email: email of the user
            password: password of the user
    """
    url = f"{API_URL}/sessions"
    data = {
        "email": email,
        "password": password
    }
    response = requests.post(url, data=data)
    assert response.status_code == 200
    assert response.json() == {'email': email, 'message': 'logged in'}
    return response.cookies["session_id"]


def profile_unlogged() -> None:
    """ Profile of an unlogged user
        Testing for the profile route when the user is not logged in
    """
    url = f"{API_URL}/profile"
    response = requests.get(url)
    assert response.status_code == 403


def profile_logged(session_id: str) -> None:
    """ Profile of a logged user
        Testing for the profile route when the user is logged in
        Args:
            session_id: session id of the user
    """
    url = f"{API_URL}/profile"
    cookies = {
        "session_id": session_id
    }
    response = requests.get(url, cookies=cookies)
    assert response.status_code == 200
    assert response.json() == {"email": EMAIL}


def log_out(session_id: str) -> None:
    """ Log out a user
        Testing for the sessions delete route
        Args:
            session_id: session id of the user
    """
    url = f"{API_URL}/sessions"
    cookies = {
        "session_id": session_id
    }
    response = requests.delete(url, cookies=cookies)
    assert response.status_code == 200


def reset_password_token(email: str) -> str:
    """ Reset password token
        Testing for the reset password route
        Args:
            email: email of the user
    """
    url = f"{API_URL}/reset_password"
    data = {
        "email": email
    }
    response = requests.post(url, data=data)
    assert response.status_code == 200
    assert response.json()["email"] == email
    assert "reset_token" in response.json()
    return response.json()["reset_token"]


def update_password(email: str, reset_token: str, new_password: str) -> None:
    """ Update user password
        Testing for the update password route
        Args:
            email: email of the user
            reset_token: reset token of the user
            new_password: new password of the user
    """
    url = f"{API_URL}/reset_password"
    data = {
        "email": email,
        "reset_token": reset_token,
        "new_password": new_password
    }
    response = requests.put(url, data=data)
    assert response.status_code == 200
    assert response.json() == {'email': email, 'message': 'Password updated'}


if __name__ == "__main__":

    register_user(EMAIL, PASSWD)
    log_in_wrong_password(EMAIL, NEW_PASSWD)
    profile_unlogged()
    session_id = log_in(EMAIL, PASSWD)
    profile_logged(session_id)
    log_out(session_id)
    reset_token = reset_password_token(EMAIL)
    update_password(EMAIL, reset_token, NEW_PASSWD)
    log_in(EMAIL, NEW_PASSWD)
