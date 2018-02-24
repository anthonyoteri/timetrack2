# Copyright (C) 2018, Anthony Oteri
# All rights reserved.

import collections
from datetime import date, datetime, timedelta
from unittest import mock

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
    create.assert_called_once_with(name='foo', description=None)


@mock.patch('tt.task.create')
def test_add_task_with_description(create, task_service):
    task_service.add('foo', 'bar')
    create.assert_called_once_with(name='foo', description='bar')


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


@mock.patch('tt.task.get')
@mock.patch('tt.task.update')
def test_rename_task(update, get, task_service, mocker):
    old_task = mocker.MagicMock(spec=Task)
    old_task.id = 1
    get.return_value = old_task

    task_service.rename('old', 'new')

    get.assert_called_once_with(name='old')
    update.assert_called_with(1, name='new')


@mock.patch('tt.task.get')
@mock.patch('tt.task.update')
def test_describe_task(update, get, task_service, mocker):
    task = mocker.MagicMock(spec=Task)
    task.id = 1
    get.return_value = task

    task_service.describe('some task', 'description')

    get.assert_called_once_with(name='some task')
    update.assert_called_with(1, description='description')


@mock.patch('tt.task.get')
@mock.patch('tt.task.update')
def test_describe_task_blank(update, get, task_service, mocker):
    task = mocker.MagicMock(spec=Task)
    task.id = 1
    get.return_value = task

    task_service.describe('some task', '')

    get.assert_called_once_with(name='some task')
    update.assert_called_with(1, description='')


@mock.patch('tt.task.tasks')
def test_list(tasks, task_service):
    expected = [('foo', None), ('bar', None), ('baz', 'bam boom')]
    tasks.return_value = [Task(name=n, description=d) for n, d in expected]

    actual = list(task_service.list())

    assert tasks.called
    assert actual == expected


@mock.patch('tt.timer.create')
def test_start(create, mocker, timer_service):

    timestamp = mocker.MagicMock(spec=datetime)
    timer_service.start('foo', timestamp)

    create.assert_called_once_with(task='foo', start=timestamp)


@mock.patch('tt.timer.create')
def test_start_raises_validation_error(create, mocker, timer_service):
    timestamp = mocker.MagicMock(spec=datetime)
    create.side_effect = ValidationError
    with pytest.raises(ValidationError):
        timer_service.start('foo', timestamp)


@mock.patch('tt.timer.active')
@mock.patch('tt.timer.update')
def test_stop_with_active(update, active, mocker, timer_service):

    timer = Timer(
        id=1, task=Task(name='foo'), start=mocker.MagicMock(spec=datetime))
    active.return_value = timer

    timestamp = mocker.MagicMock(spec=datetime)
    timer_service.stop(timestamp)

    assert active.called
    update.assert_called_once_with(1, stop=timestamp)


@mock.patch('tt.timer.active')
@mock.patch('tt.timer.update')
def test_stop_without_active(update, active, mocker, timer_service):
    active.return_value = None

    timestamp = mocker.MagicMock(spec=datetime)
    timer_service.stop(timestamp)

    assert active.called
    assert not update.called


@mock.patch('tt.timer.update')
def test_update_task(update, timer_service):
    timer_service.update(id=1, task='foo')
    update.assert_called_once_with(id=1, task='foo', start=None, stop=None)


@mock.patch('tt.timer.update')
def test_update_start(update, mocker, timer_service):
    start = mocker.MagicMock(spec=datetime)

    timer_service.update(id=1, start=start)
    update.assert_called_once_with(id=1, task=None, start=start, stop=None)


@mock.patch('tt.timer.update')
def test_update_stop(update, mocker, timer_service):
    stop = mocker.MagicMock(spec=datetime)

    timer_service.update(id=1, stop=stop)
    update.assert_called_once_with(id=1, task=None, start=None, stop=stop)


@mock.patch('tt.timer.remove')
def test_delete(remove, timer_service):
    timer_service.delete(1234)
    remove.assert_called_once_with(id=1234)


@mock.patch('tt.timer.groups_by_timerange')
def test_summary(groups_by_timerange, mocker, timer_service):
    expected = [('foo', timedelta(hours=1)), ('bar', timedelta(hours=2))]
    groups_by_timerange.return_value = iter(expected)

    begin = mocker.MagicMock(spec=datetime)
    end = mocker.MagicMock(spec=datetime)

    actual = list(timer_service.summary(range_begin=begin, range_end=end))

    groups_by_timerange.assert_called_with(start=begin, end=end)
    assert actual == expected + [('TOTAL', timedelta(hours=3))]


@mock.patch('tt.timer.timers_by_timerange')
def test_records(timers_by_timerange, mocker, timer_service):
    TimerRecord = collections.namedtuple(
        'TimerRecord', ['id', 'task', 'start_time', 'stop_time', 'elapsed'])

    expected = [
        TimerRecord(1, 'foo', '1000', '1001', timedelta(hours=1)),
        TimerRecord(2, 'bar', '1000', '1002', timedelta(hours=2))
    ]

    timers_by_timerange.return_value = iter(expected)

    begin = mocker.MagicMock(spec=datetime)
    end = mocker.MagicMock(spec=datetime)

    actual = list(timer_service.records(range_begin=begin, range_end=end))

    timers_by_timerange.assert_called_with(start=begin, end=end)
    assert actual == expected


@mock.patch('tt.timer.aggregate_by_task_date')
def test_report(agg, mocker, timer_service):

    weekly_data = {
        'foo': {
            date(2018, 2, 6): timedelta(hours=1),
            date(2018, 2, 7): timedelta(hours=2),
        },
        'bar': {
            date(2018, 2, 6): timedelta(hours=7),
            date(2018, 2, 7): timedelta(hours=6),
        },
    }

    agg.return_value = weekly_data

    range_begin = datetime(2018, 2, 5)
    range_end = datetime(2018, 2, 8)

    header, table = list(
        timer_service.report(range_begin=range_begin, range_end=range_end))[0]

    agg.assert_called_once_with(start=range_begin, end=range_end)

    expected_header = [
        ' ' * 16,
        'Feb 05',
        'Feb 06',
        'Feb 07',
        'Feb 08',
        'Feb 09',
        'Total',
    ]

    assert expected_header == header

    expected_table = [[
        'foo', None,
        timedelta(hours=1),
        timedelta(hours=2), None, None,
        timedelta(hours=3)
    ], [
        'bar', None,
        timedelta(hours=7),
        timedelta(hours=6), None, None,
        timedelta(hours=13)
    ], [
        'TOTAL', None,
        timedelta(hours=8),
        timedelta(hours=8), None, None,
        timedelta(hours=16)
    ]]

    assert expected_table == table
