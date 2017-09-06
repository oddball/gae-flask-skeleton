# -*- coding: utf-8 -*-
import functools
import sys
from base64 import decodestring
from collections import Iterable
from datetime import timedelta, datetime

import re
from google.appengine.ext import testbed
from webtest import AppError


@functools.total_ordering
class Infinity(object):
    """Compares greater than anything else; not equal to itself.

    Also allows addition/subtraction.
    """

    def __eq__(self, other):
        return False

    def __lt__(self, other):
        return False

    def __sub__(self, other):
        return self

    def __add__(self, other):
        return self


infinity = Infinity()


_TIME_SHIFT_DEFAULT = 10


def eta_delta_to_sec(eta_delta):
    """
    Convert from the task queue eta_delta format to seconds as integer.
    Examples of the eta_delta format:

        '5:59:56 from now'
        '4:38:43 ago'

    Arguments:
        eta_delta (str):
           An eta_delta string in the format described above.

    Returns:
        A timedelta object as if calculated by the following formula
            dt = NOW - ETA
        thus a task is to be executed once dt >= 0.
    """
    m = re.match(
        r'((?P<days>\d+) days, )?(?P<hours>\d+):(?P<minutes>\d+):(?P<seconds>\d+) (?P<sign>from now|ago)',
        eta_delta
    )
    if not m:
        return None
    d = m.groupdict(0)
    sign = {'ago': 1, 'from now': -1}[d.pop('sign')]
    dt = timedelta(**{key: int(value) for key, value in d.items()})
    return sign * dt.total_seconds()


def _time_shift_in_sec(time_shift):
    if isinstance(time_shift, timedelta):
        time_shift = time_shift.total_seconds()
    elif isinstance(time_shift, basestring):
        time_shift = float(time_shift)
    return time_shift


class TaskQueueProcessor(object):

    def __init__(self, test_case):
        test_case.addCleanup(self.flush)
        self.testbed = test_case.testbed
        self.task_queue = self.testbed.get_stub(testbed.TASKQUEUE_SERVICE_NAME)
        self.all_queues = [x['name'] for x in self.task_queue.GetQueues()]

    def count(self, queue_names=None):
        queue_names = queue_names or self.all_queues
        n = 0
        for queue_name in queue_names:
            q = [x for x in self.task_queue.GetQueues() if x['name']
                 == queue_name][0]
            n += q['tasks_in_queue']
        return n

    def get_tasks(self, queue_names=None):
        queue_names = queue_names or self.all_queues
        tasks = sum([self.task_queue.GetTasks(q) for q in queue_names], [])
        for task in tasks:
            task['eta_delta_sec'] = eta_delta_to_sec(task['eta_delta'])
        return tasks

    def get_ready(self, queue_names=None, time_shift=_TIME_SHIFT_DEFAULT, stop_at=None):
        """
        Get only tasks that are ready for execution, i.e. ETA is now or in the past. Do not
        execute tasks after the datetime `stop_at` (if it is given).
        """
        queue_names = queue_names or self.all_queues
        time_shift = _time_shift_in_sec(time_shift)
        stop_at_usec = (stop_at - datetime(1970, 1, 1)
                        ).total_seconds() * 10**6 if stop_at else infinity
        return filter(lambda task: task['eta_delta_sec'] + time_shift >= 0 and task['eta_usec'] < stop_at_usec,
                      self.get_tasks(queue_names))

    def get_by_url(self, url, queue_names=None):
        """Look up task by url, raise ValueError if there is more than one match"""
        queue_names = queue_names or self.all_queues
        result = None
        for task in self.get_tasks(queue_names):
            if url in task['url']:
                if result:
                    raise ValueError('Found multiple tasks for %s' % url)
                result = task
        return result

    def get_last(self, queue_name='default'):
        tasks = self.get_tasks(queue_names=(queue_name,))
        assert tasks, 'No tasks found'
        return tasks[-1]

    def delete(self, task_name, queue_name='default'):
        self.task_queue.DeleteTask(queue_name, task_name)

    def process(self, application=None, time_shift=_TIME_SHIFT_DEFAULT, stop_at=None, filter=lambda task: True,
                queue_names=None):
        """
        Process all tasks in the queue with an ETA (Estimated Time of Arrival) now or in the past.

        Argumets:
            application (WSGIApplication):
                An application containing the urls for the tasks to be executed-
            time_shift (int or datetime.timedelta):
                Amount of virtual time shift given as integer or float seconds; a string that will parse as float;
                or a datetime.timedelta object. The time shift allows for the execution of tasks with an ETA in the
                future, and may be set to 'inf' to execute all tasks in the queue.
            stop_at:
                Do not process tasks with execution time (eta) beyond this point. Should be a datetime.
            queue_name:
                If set to None, process all queues, if a tuple, process all queues in the tuple

        Returns:
            The number of tasks executed (int)
        """
        if queue_names is None:
            queue_names = self.all_queues
        if application is None:
            from main import application as tq_app
            application = [tq_app]
        if isinstance(application, Iterable):
            application = list(application)
        else:
            application = [application]
        clients = [app.test_client() for app in application]

        count = 0
        for task in self.get_ready(queue_names=queue_names, time_shift=time_shift, stop_at=stop_at):
            if not filter(task):
                continue
            e = None
            for client in clients:
                try:
                    if task['url'] == '/_ah/queue/deferred':
                        raise AssertionError('we do not use deferred in mcash')
                    getattr(client, task.get('method', 'POST').lower())(
                        str(task['url']),
                        data=decodestring(task['body']),
                        headers=dict([(k, str(v)) for k, v in task[
                                     'headers'] if k not in ('Content-Length',)]),
                        environ_overrides={'USER_IS_ADMIN': '1'}
                    )
                    self.delete(task['name'], queue_name=task['queue_name'])
                    e = None
                    count += 1
                    break
                except AppError as e:
                    e = sys.exc_info()
            if e is not None:
                raise e[0], e[1], e[2]
        return count

    def process_recursively(self, application=None, time_shift=_TIME_SHIFT_DEFAULT, stop_at=None,
                            filter=lambda task: True, queue_names=None):
        """
        Process tasks like process() but will also process subsequent tasks created while executing tasks.
        """
        n = 0
        k = -1
        while k != 0:
            k = self.process(application=application, time_shift=time_shift, stop_at=stop_at, filter=filter,
                             queue_names=queue_names)
            n += k
        return n

    def flush(self):
        for q in self.task_queue.GetQueues():
            self.task_queue.FlushQueue(q['name'])
