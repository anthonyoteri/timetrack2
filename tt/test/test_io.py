# Copyright (C) 2018, Anthony Oteri
# All rights reserved

from datetime import datetime, timedelta, timezone
import io

import pytest
from unittest import mock

import tt.service
from tt.exc import ValidationError
from tt.io import dump, load


@pytest.fixture
def timer_service(mocker):
    return mocker.MagicMock(spec=tt.service.TimerService)


@pytest.fixture
def task_service(mocker):
    return mocker.MagicMock(spec=tt.service.TaskService)


@mock.patch('json.dump')
def test_dump(json_dump, timer_service, mocker):

    out = mocker.MagicMock(spec=io.TextIOWrapper)
    start = mocker.MagicMock(spec=datetime)
    start.isoformat.return_value = '2018-01-01T00:00:00Z'
    stop = mocker.MagicMock(spec=datetime)
    elapsed = mocker.MagicMock(spec=timedelta)
    elapsed.total_seconds.return_value = 600.0

    timer_service.records.return_value = [(1, 'foo', start, stop, elapsed)]

    dump(timer_service, out)

    assert timer_service.records.called
    json_dump.assert_called_with({
        'task': 'foo',
        'start': '2018-01-01T00:00:00Z',
        'elapsed': 600
    }, out)


def test_load(task_service, timer_service):

    lines = [
        '{"task": "foo", "start": "2018-01-01T00:00:00Z", "elapsed": 600}\n',
    ]

    load(task_service, timer_service, lines)

    task_service.add.assert_called_once_with(name='foo')
    timer_service.start.assert_called_once_with(
        task='foo',
        timestamp=datetime(2018, 1, 1, 0, 0, 0, tzinfo=timezone.utc))
    timer_service.stop.assert_called_once_with(
        timestamp=datetime(2018, 1, 1, 0, 10, 0, tzinfo=timezone.utc))


def test_load_duplicate_task(task_service, timer_service):

    lines = [
        '{"task": "foo", "start": "2018-01-01T00:00:00Z", "elapsed": 600}\n',
        '{"task": "foo", "start": "2018-01-01T00:10:00Z", "elapsed": 600}\n',
    ]

    task_service.add.side_effect = None, ValidationError

    load(task_service, timer_service, lines)

    add_calls = [
        mock.call(name='foo'),
        mock.call(name='foo'),
    ]
    task_service.add.assert_has_calls(add_calls)

    start_calls = [
        mock.call(
            task='foo',
            timestamp=datetime(2018, 1, 1, 0, 0, 0, tzinfo=timezone.utc)),
        mock.call(
            task='foo',
            timestamp=datetime(2018, 1, 1, 0, 10, 0, tzinfo=timezone.utc)),
    ]
    timer_service.start.assert_has_calls(start_calls)

    stop_calls = [
        mock.call(
            timestamp=datetime(2018, 1, 1, 0, 10, 0, tzinfo=timezone.utc)),
        mock.call(
            timestamp=datetime(2018, 1, 1, 0, 20, 0, tzinfo=timezone.utc)),
    ]
    timer_service.stop.assert_has_calls(stop_calls)
