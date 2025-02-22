#!/usr/bin/env python3
"""
Route module for the API
"""
from os import getenv
from api.v1.views import app_views
from flask import Flask, jsonify, abort, request
from flask_cors import (CORS, cross_origin)
import os


app = Flask(__name__)
app.register_blueprint(app_views)
CORS(app, resources={r"/api/v1/*": {"origins": "*"}})
auth = None
auth_type = getenv('AUTH_TYPE')


if auth_type:
    from api.v1.auth.auth import Auth
    from api.v1.auth.basic_auth import BasicAuth
    from api.v1.auth.session_auth import SessionAuth
    from api.v1.auth.session_exp_auth import SessionExpAuth
    from api.v1.auth.session_db_auth import SessionDBAuth
    authentification = {
            'session_db_auth': SessionDBAuth,
            'session_exp_auth': SessionExpAuth,
            'session_auth': SessionAuth,
            'basic_auth': BasicAuth,
            'auth': Auth}
    if auth_type in authentification:
        auth = authentification[auth_type]()


@app.before_request
def before_request():
    """ Handles all before request logic
        Implements the authorization process
    """
    if not auth:
        return
    auth_paths = [
            '/api/v1/status/',
            '/api/v1/unauthorized/',
            '/api/v1/forbidden/',
            '/api/v1/auth_session/login/'
            ]
    if not auth.require_auth(request.path, auth_paths):
        return
    if not auth.authorization_header(request) \
            and not auth.session_cookie(request):
        abort(401)
    current_user = auth.current_user(request)
    if not current_user:
        abort(403)
    request.current_user = current_user


@app.errorhandler(404)
def not_found(error) -> str:
    """ Not found handler
    """
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(401)
def unauthorized(error) -> str:
    """ unauthorized handler
    """
    return jsonify({"error": "Unauthorized"}), 401


@app.errorhandler(403)
def forbidden(error) -> str:
    """ forbidden handler
    """
    return jsonify({"error": "Forbidden"}), 403


if __name__ == "__main__":
    host = getenv("API_HOST", "0.0.0.0")
    port = getenv("API_PORT", "5000")
    app.run(host=host, port=port)
