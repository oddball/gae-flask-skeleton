# -*- coding: utf-8 -*-
from flask import url_for
from google.appengine.api import taskqueue


def add_example_task():
    task = taskqueue.Task(
        url=url_for('tq.example_task'),
        target='default',
        method='GET'
    )
    task.add()


def add_cron_job_trigger_task():
    task = taskqueue.Task(
        url=url_for('tq.cron_job_trigger'),
        target='default',
        method='GET'
    )
    task.add()
