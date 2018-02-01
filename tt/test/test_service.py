# Copyright (C) 2018, Anthony Oteri
# All rights reserved.

import collections
from datetime import timedelta
from unittest import mock

import pytest

from tt.exc import ParseError, ValidationError
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


@mock.patch('dateparser.parse')
@mock.patch('tt.timer.create')
def test_start(create, parse, mocker, timer_service):
    ts = mocker.Mock()
    ts.replace.return_value = 'value'
    parse.return_value = ts

    timer_service.start('foo', 'now')

    parse.assert_called_once_with('now', settings=mock.ANY)
    ts.replace.assert_called_once_with(microsecond=0)
    create.assert_called_once_with(task='foo', start='value')


@mock.patch('tt.timer.create')
def test_start_raises_validation_error(create, timer_service):
    create.side_effect = ValidationError
    with pytest.raises(ValidationError):
        timer_service.start('foo', 'now')


@mock.patch('dateparser.parse')
@mock.patch('tt.timer.active')
@mock.patch('tt.timer.update')
def test_stop_with_active(update, active, parse, mocker, timer_service):
    ts = mocker.Mock()
    ts.replace.return_value = 'value'
    parse.return_value = ts

    timer = Timer(id=1, task=Task(name='foo'), start=mocker.Mock())
    active.return_value = timer

    timer_service.stop('now')

    parse.assert_called_once_with('now', settings=mock.ANY)
    ts.replace.assert_called_once_with(microsecond=0)
    assert active.called
    update.assert_called_once_with(1, stop='value')


@mock.patch('dateparser.parse')
@mock.patch('tt.timer.active')
@mock.patch('tt.timer.update')
def test_stop_without_active(update, active, parse, mocker, timer_service):
    ts = mocker.Mock()
    ts.replace.return_value = 'value'
    parse.return_value = ts

    active.return_value = None

    timer_service.stop('now')

    parse.assert_called_once_with('now', settings=mock.ANY)
    ts.replace.assert_called_once_with(microsecond=0)
    assert active.called
    assert not update.called


@mock.patch('dateparser.parse')
def test_parse_timestamp_raises_parse_error(parse, timer_service):
    parse.return_value = None
    with pytest.raises(ParseError):
        timer_service._parse_timestamp('foo')


@mock.patch('tt.timer.groups_by_timerange')
def test_summary(groups_by_timerange, timer_service):
    expected = [('foo', timedelta(hours=1)), ('bar', timedelta(hours=2))]
    groups_by_timerange.return_value = iter(expected)

    actual = list(
        timer_service.summary(range_begin='earlier', range_end='later'))

    groups_by_timerange.assert_called_with(start='earlier', end='later')
    assert actual == expected


@mock.patch('tt.timer.timers_by_timerange')
def test_records(timers_by_timerange, timer_service):
    TimerRecord = collections.namedtuple(
        'TimerRecord', ['id', 'task', 'start_time', 'stop_time', 'elapsed'])

    expected = [
        TimerRecord(1, 'foo', '1000', '1001', timedelta(hours=1)),
        TimerRecord(2, 'bar', '1000', '1002', timedelta(hours=2))
    ]

    timers_by_timerange.return_value = iter(expected)

    actual = list(
        timer_service.records(range_begin='earlier', range_end='later'))

    timers_by_timerange.assert_called_with(start='earlier', end='later')
    assert actual == expected
