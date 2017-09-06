# -*- coding: utf-8 -*-
import string
import random

from google.appengine.ext import ndb
from werkzeug.security import generate_password_hash
from flask_security import UserMixin


def generate_id(size=10, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


import settings


def generate_id(size=10, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


class EntityAlreadyExists(Exception):
    pass


class EntityNotFound(Exception):
    pass


class FailedUniqueIDGeneration(Exception):
    pass


class NeedsDebugException(Exception):
    pass


class BaseModel(ndb.Model):
    date_created = ndb.DateTimeProperty(auto_now_add=True)
    date_modified = ndb.DateTimeProperty(auto_now=True)
    model_version = ndb.IntegerProperty(default=0)


class JustToShow(BaseModel):
    _use_memcache = False

    @classmethod
    def compute_key(cls, id):
        return ndb.Key(cls, id)

    @classmethod
    @ndb.transactional
    def create_and_put(cls, **kwargs):
        key = None
        for i in xrange(101):
            key = ndb.Key(cls, '{}'.format(generate_id()))
            if i == 100:
                raise FailedUniqueIDGeneration
            else:
                if not key.get():
                    break

        model = cls(key=key, **kwargs)
        model.put()
        return model


class User(UserMixin, BaseModel):
    first_name = ndb.StringProperty(default='')
    last_name = ndb.StringProperty(default='')
    cn = ndb.StringProperty(required=False)
    if (settings.TESTBED_ACTIVE):
        password = ndb.StringProperty(default=None)
    email = ndb.StringProperty(default=None)

    @property
    def login(self):
        return self.key.id()

    @property
    def active(self):
        return True  # https://flask-login.readthedocs.io/en/latest/#your-user-class

    @property
    def user_id(self):
        return self.key.id()

    def get_id(self):
        return self.key.id()

    @classmethod
    def compute_key(cls, user_id):
        return ndb.Key(cls, user_id)

    @classmethod
    @ndb.transactional_tasklet
    def create_and_put_async(cls, user_id, **kwargs):
        key = cls.compute_key(user_id)
        if (yield key.get_async()):
            raise EntityAlreadyExists(key)
        user = cls(key=key, **kwargs)
        yield user.put_async()
        raise ndb.Return(user)

    @classmethod
    @ndb.transactional
    def create_and_put(cls, user_id, **kwargs):
        key = cls.compute_key(user_id)
        if key.get():
            raise EntityAlreadyExists(key)
        user = cls(key=key, **kwargs)
        user.put()
        return user

    @classmethod
    @ndb.transactional
    def create_and_put_test_user(cls, **kwargs):
        key = None
        for i in xrange(101):
            key = ndb.Key(cls, '{}'.format(generate_id()))
            if i == 100:
                raise FailedUniqueIDGeneration
            else:
                if not key.get():
                    break

        user = cls(key=key, **kwargs)
        user.put()
        return user
