# Copyright (C) 2018, Anthony Oteri
# All rights reserved.

import pytest

from tt.exc import ParseError, ValidationError
from tt.orm import Task, Timer
from tt.service import TaskService, TimerService


@pytest.fixture
def task_service(session):
    return TaskService()


@pytest.fixture
def timer_service(session):
    return TimerService()


def test_add_task(session, task_service):
    task_service.add('foo')
    assert session.query(Task).filter(Task.name == 'foo').count() == 1


def test_remove_task(session, task_service):
    test_add_task(session, task_service)

    task_service.remove('foo')
    assert session.query(Task).filter(Task.name == 'foo').count() == 0


def test_list_tasks(session, task_service):
    for name in ('foo', 'bar', 'baz'):
        task_service.add(name)

    assert session.query(Task).count() == 3

    tasks = list(task_service.list())
    assert tasks == ['foo', 'bar', 'baz']


@pytest.mark.parametrize('timestamp', [
    'now',
    'a week ago',
    'yesterday at noon',
    '2017-12-31T00:00:00',
    '2 days ago',
    '2 hours and 5 minutes ago',
    'yesterday at 16:00',
    'yesterday at 4pm',
])
def test_start_timer(timestamp, session, task_service, timer_service):
    task_service.add('foo')
    timer_service.start('foo', timestamp)

    assert session.query(Timer).count() == 1


def test_start_timer_parse_error(task_service, timer_service):
    task_service.add('foo')
    with pytest.raises(ParseError):
        timer_service.start('foo', 'a long time ago in a galaxy far away')


def test_start_timer_in_the_future(task_service, timer_service):
    task_service.add('foo')
    with pytest.raises(ValidationError):
        timer_service.start('foo', 'next week')


def test_stop_timer(session, task_service, timer_service):
    task_service.add('foo')
    timer_service.start('foo', 'an hour ago')
    timer_service.stop()

    last = session.query(Timer).get(1)
    assert last.stop is not None


def test_stop_timer_in_the_past(session, task_service, timer_service):
    task_service.add('foo')
    timer_service.start('foo', 'an hour ago')
    with pytest.raises(ValidationError):
        timer_service.stop('2 hours ago')
