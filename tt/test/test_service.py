# Copyright (C) 2018, Anthony Oteri
# All rights reserved.

import collections
from datetime import timedelta
try:
    from unittest import mock
except ImportError:
    import mock

import pytest

from tt.exc import ValidationError
from tt.orm import Task, Timer
from tt.service import TaskService, TimerService


@pytest.fixture
def task_service():
    return TaskService()


@pytest.fixture
def timer_service():
    return TimerService()


@mock.patch('tt.task.create')
def test_add_task(create, task_service):
    task_service.add('foo')
    create.assert_called_once_with(name='foo')


@mock.patch('tt.task.create')
def test_add_validation_error(create, task_service):
    create.side_effect = ValidationError
    with pytest.raises(ValidationError):
        task_service.add('foo')


@mock.patch('tt.task.remove')
def test_remove_task(remove, task_service):
    task_service.remove('foo')
    remove.assert_called_once_with(name='foo')


@mock.patch('tt.task.remove')
def test_remove_validation_error(remove, task_service):
    remove.side_effect = ValidationError
    with pytest.raises(ValidationError):
        task_service.remove('foo')


@mock.patch('tt.task.tasks')
def test_list(tasks, task_service):
    expected = ['foo', 'bar', 'baz']
    tasks.return_value = [Task(name=n) for n in expected]

    actual = list(task_service.list())

    assert tasks.called
    assert actual == expected


@mock.patch('tt.timer.create')
def test_start(create, mocker, timer_service):

    timestamp = mocker.Mock()
    timer_service.start('foo', timestamp)

    create.assert_called_once_with(task='foo', start=timestamp)


@mock.patch('tt.timer.create')
def test_start_raises_validation_error(create, mocker, timer_service):
    timestamp = mocker.Mock()
    create.side_effect = ValidationError
    with pytest.raises(ValidationError):
        timer_service.start('foo', timestamp)


@mock.patch('tt.timer.active')
@mock.patch('tt.timer.update')
def test_stop_with_active(update, active, mocker, timer_service):

    timer = Timer(id=1, task=Task(name='foo'), start=mocker.Mock())
    active.return_value = timer

    timestamp = mocker.Mock()
    timer_service.stop(timestamp)

    assert active.called
    update.assert_called_once_with(1, stop=timestamp)


@mock.patch('tt.timer.active')
@mock.patch('tt.timer.update')
def test_stop_without_active(update, active, mocker, timer_service):
    active.return_value = None

    timestamp = mocker.Mock()
    timer_service.stop(timestamp)

    assert active.called
    assert not update.called


@mock.patch('tt.timer.groups_by_timerange')
def test_summary(groups_by_timerange, mocker, timer_service):
    expected = [('foo', timedelta(hours=1)), ('bar', timedelta(hours=2))]
    groups_by_timerange.return_value = iter(expected)

    begin = mocker.Mock()
    end = mocker.Mock()

    actual = list(timer_service.summary(range_begin=begin, range_end=end))

    groups_by_timerange.assert_called_with(start=begin, end=end)
    assert actual == expected


@mock.patch('tt.timer.timers_by_timerange')
def test_records(timers_by_timerange, mocker, timer_service):
    TimerRecord = collections.namedtuple(
        'TimerRecord', ['id', 'task', 'start_time', 'stop_time', 'elapsed'])

    expected = [
        TimerRecord(1, 'foo', '1000', '1001', timedelta(hours=1)),
        TimerRecord(2, 'bar', '1000', '1002', timedelta(hours=2))
    ]

    timers_by_timerange.return_value = iter(expected)

    begin = mocker.Mock()
    end = mocker.Mock()

    actual = list(timer_service.records(range_begin=begin, range_end=end))

    timers_by_timerange.assert_called_with(start=begin, end=end)
    assert actual == expected
