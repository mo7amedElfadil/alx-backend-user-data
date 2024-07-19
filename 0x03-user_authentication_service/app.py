#!/usr/bin/env python3
""" Flask app to serve the model as an API. """
from auth import Auth
from flask import Flask, abort, jsonify, redirect, request

AUTH = Auth()
app = Flask(__name__)
app.url_map.strict_slashes = False


@app.route("/", methods=["GET"])
def greet():
    """ Greeting message. """
    return jsonify({"message": "Bienvenue"})


@app.route("/users", methods=["POST"])
def users():
    """ POST /users route to register a user.
        - email: user email
        - password: user password
        Returns:
            - 400 if email or password is missing
            - 200 and the user email if the user was created
            - 400 if the user already exists
    """
    email = request.form.get("email")
    password = request.form.get("password")

    if not email or not password:
        abort(400)

    try:
        user = AUTH.register_user(email, password)
    except ValueError:
        return jsonify({"message": "email already registered"}), 400

    return jsonify({"email": user.email, "message": "user created"}), 200


@app.route("/sessions", methods=["POST"])
def login():
    """ POST /sessions route to login a user.
        - email: user email
        - password: user password
        Returns:
            - 400 if email or password is missing
            - 200 and the session id if the user was logged in
            - 401 if the user does not exist or the password is invalid
    """
    email = request.form.get("email")
    password = request.form.get("password")

    if not AUTH.valid_login(email, password):
        abort(401)

    session_id = AUTH.create_session(email)
    response = jsonify({"email": email, "message": "logged in"})
    response.set_cookie("session_id", session_id)

    return response


@app.route("/sessions", methods=["DELETE"])
def logout():
    """ DELETE /sessions route to logout a user.
        - session_id: user session id
        Returns:
            - 403 if the session id is invalid
            - 302 and redirect to the main page if the session was deleted
    """
    session_id = request.cookies.get("session_id", None)

    if not session_id:
        abort(403)

    user = AUTH.get_user_from_session_id(session_id)

    if not user:
        abort(403)

    AUTH.destroy_session(user.id)
    return redirect("/")


@app.route("/profile", methods=["GET"])
def profile():
    """ GET /profile route to obtain user email.
        - session_id: user session id
        Returns:
            - 403 if the session id is invalid
            - 200 and the user email if the session is valid
    """

    session_id = request.cookies.get("session_id", None)

    if not session_id:
        abort(403)

    user = AUTH.get_user_from_session_id(session_id)

    if not user:
        abort(403)

    return jsonify({"email": user.email}), 200


@app.route("/reset_password", methods=["POST"])
def get_reset_password_token():
    """ POST /reset_password route to generate a reset password token.
        - email: user email
        Returns:
            - 400 if email is missing
            - 403 if the email does not exist
            - 200 and the reset token if the token was generated
    """
    email = request.form.get("email")

    try:
        reset_token = AUTH.get_reset_password_token(email)
    except ValueError:
        abort(403)

    return jsonify({"email": email, "reset_token": reset_token}), 200


@app.route("/reset_password", methods=["PUT"])
def update_password():
    """ PUT /reset_password route to update the user password.
        - email: user email
        - reset_token: user reset token
        - new_password: user new password
        Returns:
            - 403 if the email does not exist or the reset token is invalid
            - 200 if the password was updated
    """
    import uuid
    email = request.form.get("email")
    reset_token = request.form.get("reset_token")
    new_password = request.form.get("new_password")
    try:
        uuid.UUID(reset_token)
        AUTH.update_password(reset_token, new_password)
    except ValueError:
        abort(403)
    return jsonify({"email": email, "message": "Password updated"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000")
