# -*- coding: utf-8 -*-
import logging
import json
from pprint import pformat

from flask import Flask, request
from flask.testing import FlaskClient
from flask_bootstrap import Bootstrap
from flask_login import LoginManager

from models import User
import settings


def create_app(name, *args, **kwargs):
    app = Flask(name, *args, **kwargs)
    app.test_client_class = FlaskClient
    app.secret_key = settings.SECRET_KEY
    Bootstrap(app)

    @app.before_request
    def before_request():
        try:
            data = pformat(json.loads(request.data))
        except:
            data = str(request.data)
        logging.debug('REQUEST\nHEADERS %s\nBODY %s', request.headers, data)

    @app.after_request
    def after_request(resp):
        try:
            data = pformat(json.loads(resp.data))
        except:
            data = str(resp.data)
        logging.debug('RESPONSE\nHEADERS %s\nBODY %s', resp.headers, data)
        return resp

    app.debug = settings.DEBUG

    # Initialize flask-login
    def init_login():
        login_manager = LoginManager()
        login_manager.init_app(app)
        login_manager.login_view = "/login"

        # Create user loader function
        @login_manager.user_loader
        def load_user(user_id):
            key = User.compute_key(user_id=user_id)
            user = key.get()
            return user

    init_login()
    app.config.from_object(settings)

    app.jinja_env.globals['sorted'] = sorted

    return app
