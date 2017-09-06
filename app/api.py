# -*- coding: utf-8 -*-
import httplib
import json

import flask
from google.appengine.ext import ndb
from flask_login import login_user
from flask_login import current_user
from flask_login import logout_user
from route_decorators import user_required
from tqueue_add_tasks import add_example_task
from schemas import validate_input
from schemas import validate_output
from schemas import profile_in_schema
from schemas import profile_out_schema
from models import User
import settings

api_bp = flask.Blueprint("api", "api")
route = api_bp.route


@route('/info', methods=['GET'])
@ndb.synctasklet
def info():
    raise ndb.Return(json.dumps({}), httplib.OK)


@route('/data', methods=['GET'])
@ndb.synctasklet
@user_required
def data():
    raise ndb.Return(json.dumps({}), httplib.OK)


@route('/start_a_task', methods=['GET'])
@ndb.synctasklet
def start_a_task():
    add_example_task()
    raise ndb.Return(json.dumps({}), httplib.OK)


if settings.TESTBED_ACTIVE:

    @route('/create_test_user', methods=['POST'])
    @validate_input(profile_in_schema)
    @validate_output(profile_out_schema)
    @ndb.synctasklet
    def create_test_user():

        @ndb.transactional()
        def txn():
            data = flask.request.get_json()
            data.pop('id', None)
            user = User.create_and_put_test_user(**data)
            user.put()
            return user

        user = txn()
        login_user(user, remember=True)

        raise ndb.Return(json.dumps({u'first_name': user.first_name,
                                     u'last_name': user.last_name,
                                     u'id': user.key.id()}), httplib.CREATED)

    @route('/logout_test_user', methods=['PUT'])
    @ndb.synctasklet
    @user_required
    def logout():
        if current_user.is_authenticated:
            logout_user()
        raise ndb.Return(json.dumps({}), httplib.OK)