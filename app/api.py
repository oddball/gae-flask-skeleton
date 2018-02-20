# -*- coding: utf-8 -*-
import httplib
import json

from google.appengine.ext import ndb
import flask
from flask_restplus import Api
from flask_restplus import Resource
from flask_restplus import fields
from flask_login import login_user
from flask_login import current_user
from flask_login import logout_user

from route_decorators import user_required
from tqueue_add_tasks import add_example_task
from schemas import validate_input
from schemas import validate_output
from schemas import PROFILE_IN_SCHEMA
from schemas import PROFILE_OUT_SCHEMA
from models import User
import settings

api_bp = flask.Blueprint('api', __name__)
api = Api(api_bp, doc='/swagger/')

TEST_USER_IN = api.schema_model('TestUserRequest', PROFILE_IN_SCHEMA)
TEST_USER_OUT = api.schema_model('TestUserResponse', PROFILE_OUT_SCHEMA)

info_fields = api.model('Info', {
    'name': fields.String,
})


@api.route('/info')
class Info(Resource):
    @ndb.synctasklet
    @api.expect(info_fields)
    @api.marshal_with(info_fields, as_list=True)
    def get(self):
        raise ndb.Return({}, httplib.OK)


@api.route('/data')
class Data(Resource):
    @ndb.synctasklet
    @user_required
    def get(self):
        raise ndb.Return(json.dumps({}), httplib.OK)


@api.route('/start_a_task')
class StartTask(Resource):
    @ndb.synctasklet
    def post(self):
        add_example_task()
        raise ndb.Return(json.dumps({}), httplib.OK)


if settings.TESTBED_ACTIVE:

    @api.route('/create_test_user')
    class TestUser(Resource):
        @api.expect(TEST_USER_IN)
        @api.response(201, 'Created', model=TEST_USER_OUT)
        # @api.marshal_with(TEST_USER_OUT)
        @validate_input(PROFILE_IN_SCHEMA)
        @validate_output(PROFILE_OUT_SCHEMA)
        @ndb.synctasklet
        def post(self):
            @ndb.transactional()
            def txn():
                data = flask.request.get_json()
                data.pop('id', None)
                user = User.create_and_put_test_user(**data)
                user.put()
                return user

            user = txn()
            login_user(user, remember=True)

            raise ndb.Return({u'first_name': user.first_name,
                              u'last_name': user.last_name,
                              u'id': user.key.id()}, httplib.CREATED)


    @api.route('/logout_test_user')
    class LogOutTestUser(Resource):

        @ndb.synctasklet
        @user_required
        def put(self):
            if current_user.is_authenticated:
                logout_user()

            raise ndb.Return({}, httplib.OK)
