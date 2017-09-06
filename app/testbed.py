# -*- coding: utf-8 -*-
from google.appengine.ext import ndb
import flask


testbed_bp = flask.Blueprint('testbed', 'testbed')
route = testbed_bp.route


@route('/', methods=['GET'])
@ndb.synctasklet
def testbed():
    raise ndb.Return(flask.render_template('testbed.html'))
