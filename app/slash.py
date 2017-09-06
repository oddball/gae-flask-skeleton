# -*- coding: utf-8 -*-
import httplib

from flask import Blueprint, make_response
from google.appengine.ext import ndb
from google.appengine.ext import blobstore

import flask
from flask_login import login_required
from flask_login import current_user

slash_bp = Blueprint("slash", "slash")
route = slash_bp.route


@route('/', methods=['GET'])
@ndb.synctasklet
def slash():
    raise ndb.Return(flask.render_template('slash.html'))
