#!/usr/bin/env python3
""" Flask app to serve the model as an API. """
from flask import Flask, request, jsonify, abort, redirect
from auth import Auth

app = Flask(__name__)
app.url_map.strict_slashes = False
AUTH = Auth()


def verify_data(data):
    """ Verify the data sent by the user. """
    required_fields = ['email', 'password']
    if not all([field in data for field in required_fields]):
        return None
    return data['email'], data['password']


@app.route('/', methods=['GET'])
def greet():
    """ Greeting message. """
    return jsonify({'message': 'Bienvenue'})


@app.route('/users', methods=['POST'])
def users() -> str:
    """ POST /users route to register a user.
        - email: user email
        - password: user password
        Returns:
            - 400 if email or password is missing
            - 200 and the user email if the user was created
            - 400 if the user already exists
    """
    data = verify_data(request.form)
    if not data:
        return jsonify({'message': 'Bad request'}), 400
    email, password = data
    try:
        user = AUTH.register_user(email, password)
        return jsonify({'email': user.email,
                        'message': 'user created'}), 200
    except ValueError:
        return jsonify({'message': f"email already registered"}), 400


@app.route('/sessions', methods=['POST'])
def login() -> str:
    """ POST /sessions route to login a user.
        - email: user email
        - password: user password
        Returns:
            - 400 if email or password is missing
            - 200 and the session id if the user was logged in
            - 401 if the user does not exist or the password is invalid
    """
    data = verify_data(request.form)
    if not data:
        return jsonify({'message': 'Bad request'}), 400
    email, password = data
    if not AUTH.valid_login(email, password):
        abort(401)
    session_id = AUTH.create_session(email)
    response = jsonify({'email': email, 'message': 'logged in'})
    response.set_cookie('session_id', session_id)
    return response, 200


@app.route('/sessions', methods=['DELETE'])
def logout() -> str:
    """ DELETE /sessions route to logout a user.
        - session_id: user session id
        Returns:
            - 403 if the session id is invalid
            - 302 and redirect to the main page if the session was deleted
    """
    session_id = request.cookies.get('session_id')
    user = AUTH.get_user_from_session_id(session_id)
    if not user:
        abort(403)
    AUTH.destroy_session(user.id)
    return redirect('/')


@app.route('/profile', methods=['GET'])
def profile() -> str:
    session_id = request.cookies.get('session_id')
    user = AUTH.get_user_from_session_id(session_id)
    if not user:
        abort(403)
    return jsonify({'email': user.email}), 200


@app.route('/reset_password', methods=['POST'])
def get_reset_password_token() -> str:
    """ POST /reset_password route to generate a reset password token.
        - email: user email
        Returns:
            - 400 if email is missing
            - 403 if the email does not exist
            - 200 and the reset token if the token was generated
    """
    email = request.form.get('email')
    if not email:
        return jsonify({'message': 'Bad request'}), 400
    try:
        reset_token = AUTH.get_reset_password_token(email)
        return jsonify({'email': email, 'reset_token': reset_token}), 200
    except ValueError:
        abort(403)

@app.route('/reset_password', methods=['PUT'])
def update_password() -> str:
    """ PUT /reset_password route to update the user password.
        - email: user email
        - reset_token: user reset token
        - new_password: user new password
        Returns:
            - 400 if email, reset_token or new_password is missing
            - 403 if the email does not exist or the reset token is invalid
            - 200 if the password was updated
    """
    email = request.form.get('email')
    reset_token = request.form.get('reset_token')
    new_password = request.form.get('new_password')
    try:
        AUTH.update_password(reset_token, new_password)
        return jsonify({'email': email, 'message': 'Password updated'}), 200
    except ValueError:
        abort(403)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
