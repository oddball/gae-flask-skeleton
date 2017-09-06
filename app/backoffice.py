# -*- coding: utf-8 -*-
import logging
import httplib

from flask import Blueprint
from google.appengine.ext import ndb
import flask
from flask_login import login_user
from flask_login import logout_user
from flask_login import login_required
from flask_login import current_user

from models import User
import settings

backoffice_bp = Blueprint('backoffice', 'backoffice')
route = backoffice_bp.route


@route('/', methods=['GET'])
def backoffice():
    if not current_user.is_authenticated:
        return flask.redirect(flask.url_for('backoffice.login'))
    elif not current_user.key.id() in settings.ADMINS:
        return flask.redirect(flask.url_for('backoffice.login'))

    return flask.render_template('backoffice.html')


@route('/login', methods=['GET'])
@ndb.synctasklet
def login():
    # login_user(user, remember=True)
    raise flask.abort(httplib.BAD_REQUEST, 'Not implemented yet')


@route('/logout', methods=['POST', 'GET'])
@ndb.synctasklet
@login_required
def logout():
    logout_user()
    raise ndb.Return(flask.redirect(flask.url_for('backoffice.login')))


@route('/users', methods=['GET'])
@ndb.synctasklet
@login_required
def users():
    if not current_user.key.id() in settings.ADMINS:
        raise flask.abort(httplib.NOT_FOUND)

    cursor = flask.request.args.get('cursor', None)
    cursor = cursor and ndb.Cursor(urlsafe=cursor) or None
    reverse = flask.request.args.get('reverse', False)
    cursor_prev, cursor_next = cursor and cursor.reversed(), cursor
    query = User.query()
    f_order = -User.date_created
    r_order = User.date_created
    limit = 20
    if reverse:
        cursor_prev, cursor_next = cursor_next, cursor_prev
        users, cursor_prev, more = query.order(
            r_order).fetch_page(limit, start_cursor=cursor_prev)
        users.reverse()
        cursor_prev = None if not more else cursor_prev.urlsafe()
    else:
        users, cursor_next, more = query.order(
            f_order).fetch_page(limit, start_cursor=cursor_next)
        cursor_next = None if not more else cursor_next.urlsafe()

    raise ndb.Return(flask.render_template('backoffice_users.html',
                                           users=users,
                                           cursor_prev=cursor_prev,
                                           cursor_next=cursor_next
                                           ))
