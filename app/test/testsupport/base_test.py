# -*- coding: utf-8 -*-
import logging
from pprint import pformat
import httplib
import unittest

from flask import json
from google.appengine.ext import ndb
from google.appengine.ext import testbed
from google.appengine.datastore import datastore_stub_util

from main import application
from test.testsupport.task_queue import TaskQueueProcessor
from test.testsupport import urlfetch_intercept
from test.testsupport.mock_application import MockApplication


class BaseTest(unittest.TestCase):

    def setUp(self):
        # First, create an instance of the Testbed class.
        self.testbed = testbed.Testbed()
        self.testbed.setup_env()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        # root_path must be set the the location of queue.yaml.
        # Otherwise, only the 'default' queue will be available.
        self.testbed.init_taskqueue_stub()
        self.taskqueue_stub = self.testbed.get_stub(
            testbed.TASKQUEUE_SERVICE_NAME)

        self.testbed.init_blobstore_stub()
        self.testbed.init_search_stub()
        # Create a consistency policy that will simulate the High Replication
        # consistency model.
        self.policy = datastore_stub_util.PseudoRandomHRConsistencyPolicy(
            probability=1)
        # Initialize the datastore stub with this policy.
        self.testbed.init_datastore_v3_stub(consistency_policy=self.policy,
                                            use_sqlite=True, auto_id_policy=datastore_stub_util.SCATTERED)
        # Next, declare which service stubs you want to use.
        self.testbed.init_memcache_stub()
        self.testbed.init_urlfetch_stub()
        # Clear ndb's in-context cache between tests.
        # This prevents data from leaking between tests.
        # Alternatively, you could disable caching by
        # using ndb.get_context().set_cache_policy(False)
        ndb.get_context().clear_cache()
        application.config.update(SESSION_COOKIE_DOMAIN=None,
                                  testing=True)
        self.application = application
        self.test_client = application.test_client()

        # Add task queue processor
        self.task_queue = TaskQueueProcessor(self)

        urlfetch_intercept.install()
        self.addCleanup(urlfetch_intercept.uninstall)

        self.mock_pusher = MockApplication()
        self.mock_pusher.cannedresponse = ((200, {}), json.dumps({}))
        self.add_intercept('api.pusherapp.com:443', self.mock_pusher)

        self.mock_gcm = MockApplication()
        self.mock_gcm.cannedresponse = ((200, {}), json.dumps({}))
        self.add_intercept('gcm-http.googleapis.com', self.mock_gcm)

    def add_intercept(self, baseurl, mockingapp):
        urlfetch_intercept.add_intercept(baseurl, mockingapp)

    def tearDown(self):
        self.testbed.deactivate()

    def flushTaskQueue(self):
        for q in self.taskqueue_stub.GetQueues():
            self.taskqueue_stub.FlushQueue(q['name'])
