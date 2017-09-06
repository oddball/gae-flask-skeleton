# -*- coding: utf-8 -*-
import logging
import httplib

from flask import json
from flask_login import current_user

from test.testsupport.base_test import BaseTest
from models import JustToShow
from models import User


class Testcases(BaseTest):
    def test_backoffice(self):
        with self.test_client as c:
            self.assertEqual(None, current_user)
            resp = c.get(
                '/backoffice/',
            )
            self.assertEqual(httplib.FOUND, resp.status_code, msg=resp.data)

    def test_testbed(self):
        with self.test_client as c:
            self.assertEqual(None, current_user)
            resp = c.get(
                '/testbed/',
            )
            self.assertEqual(httplib.OK, resp.status_code, msg=resp.data)

    def test_api(self):
        with self.test_client as c:
            self.assertEqual(None, current_user)
            resp = c.get(
                '/api/info',
            )
            self.assertEqual(httplib.OK, resp.status_code, msg=resp.data)

    def test_api_data(self):
        with self.test_client as c:
            self.assertEqual(None, current_user)
            resp = c.get(
                '/api/data',
            )
            self.assertEqual(httplib.UNAUTHORIZED, resp.status_code, msg=resp.data)
            data = json.loads(resp.data)
            self.assertEqual(data, {"message": "UNAUTHORIZED"})

    def test_task_queue(self):
        with self.test_client as c:
            self.assertEqual(None, current_user)
            objs = JustToShow.query().fetch()
            self.assertEqual(len(objs), 0)
            resp = c.get(
                '/api/start_a_task',
            )
            self.assertEqual(httplib.OK, resp.status_code, msg=resp.data)
            self.task_queue.process()
            objs = JustToShow.query().fetch(use_cache=False, use_memcache=False)
            self.assertEqual(len(objs), 1)

    def test_slash(self):
        with self.test_client as c:
            self.assertEqual(None, current_user)
            resp = c.get(
                '/',
            )
            self.assertEqual(httplib.OK, resp.status_code, msg=resp.data)

    def test_create_test_user(self):
        with self.test_client as c:
            self.assertEqual(None, current_user)
            resp = c.post(
                '/api/create_test_user',
                data=json.dumps({u'first_name': u'John', u'last_name': u'Doe'}),
                headers={'Content-Type': 'application/json; charset=utf-8'}
            )
            self.assertEqual(httplib.CREATED, resp.status_code, msg=resp.data)
            data = json.loads(resp.data)
            user_id = data['id']
            user = User.compute_key(user_id).get()
            self.assertEqual(user, current_user)
            resp = c.get(
                '/api/data',
            )
            self.assertEqual(httplib.OK, resp.status_code)
            resp = c.put(
                '/api/logout_test_user',
            )
            self.assertEqual(httplib.OK, resp.status_code, msg=resp.data)
