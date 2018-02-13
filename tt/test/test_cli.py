# Copyright (C) 2017, Anthony Oteri
# All rights reserved.

import calendar
from datetime import datetime, timedelta, timezone
import logging
import io
from unittest import mock

import pytest

import tt.cli
from tt.exc import ParseError


@pytest.fixture
def task_service(mocker):
    init = mocker.patch('tt.cli.TaskService')
    service = mocker.Mock()
    init.return_value = service
    return service


@pytest.fixture
def timer_service(mocker):
    init = mocker.patch('tt.cli.TimerService')
    service = mocker.Mock()
    init.return_value = service
    return service


@pytest.mark.parametrize('verbose', [True, False])
@mock.patch('logging.basicConfig')
def test_configure_logging(basic_config, verbose):
    tt.cli.configure_logging(verbose=verbose)

    if verbose:
        basic_config.assert_called_once_with(level=logging.DEBUG)
    else:
        basic_config.assert_called_once_with(
            level=logging.WARNING, format=mock.ANY)


@pytest.mark.parametrize('options', [
    ['create', 'foo'],
])
def test_create(options, task_service):
    tt.cli.main(options)
    task_service.add.assert_called_with(name=options[1])


@pytest.mark.parametrize('options', [
    ['tasks'],
])
def test_tasks(options, mocker, task_service):
    task_service.list.return_value = iter(['foo', 'bar', 'bam'])
    tt.cli.main(options)
    assert task_service.list.called


@pytest.mark.parametrize('options', [
    ['remove', 'foo'],
])
def test_remove(options, mocker, task_service):
    tt.cli.main(options)
    task_service.remove.assert_called_with(name=options[1])


@pytest.mark.parametrize('options', [
    ['start', 'foo', 'one day ago'],
    ['start', 'foo'],
])
@mock.patch('dateparser.parse')
def test_start(parse, options, mocker, timer_service):

    timestamp = mocker.Mock()
    parse.return_value = timestamp

    tt.cli.main(options)

    if len(options) == 3:
        parse.assert_called_with(
            options[2], settings=tt.cli.DATEPARSER_SETTINGS)
    else:
        parse.assert_called_with('now', settings=tt.cli.DATEPARSER_SETTINGS)

    timer_service.start.assert_called_with(
        task=options[1], timestamp=timestamp.replace())


@pytest.mark.parametrize('options', [['stop', 'now'], ['stop']])
@mock.patch('dateparser.parse')
def test_stop(parse, options, mocker, timer_service):

    timestamp = mocker.Mock()
    parse.return_value = timestamp

    tt.cli.main(options)

    if len(options) == 2:
        parse.assert_called_with(
            options[1], settings=tt.cli.DATEPARSER_SETTINGS)
    else:
        parse.assert_called_with('now', settings=tt.cli.DATEPARSER_SETTINGS)

    timer_service.stop.assert_called_with(timestamp=timestamp.replace())


@pytest.mark.parametrize(
    'options', [['summary', '--begin', 'one week ago', '--end', 'now'], [
        'summary', '--begin', 'one week ago'
    ], ['summary', '--end', 'now'], ['summary']])
@mock.patch('dateparser.parse')
def test_summary(parse, options, mocker, timer_service):
    timer_service.summary.return_value = (['foo', timedelta(hours=1)],
                                          ['bar', timedelta(hours=2)])

    begin = mocker.Mock()
    end = mocker.Mock()
    parse.side_effect = (begin, end)

    tt.cli.main(options)

    calls = [tt.cli.DEFAULT_REPORT_START, tt.cli.DEFAULT_REPORT_END]
    if len(options) == 5:
        calls = [options[2], options[4]]
    elif len(options) == 3:
        if options[1] == '--begin':
            calls[0] = options[2]
        else:
            calls[1] = options[2]

    parse.assert_has_calls(
        [mock.call(ts, settings=tt.cli.DATEPARSER_SETTINGS) for ts in calls])

    timer_service.summary.assert_called_with(
        range_begin=begin.replace(), range_end=end.replace())


@pytest.mark.parametrize(
    'options', [['records', '--begin', 'one week ago', '--end', 'now'], [
        'records', '--begin', 'one week ago'
    ], ['records', '--end', 'now'], ['records']])
@mock.patch('dateparser.parse')
def test_records(parse, options, mocker, timer_service):
    timer_service.records.return_value = ([
        1, 'foo', mocker.Mock(),
        mocker.Mock(),
        timedelta(hours=1)
    ], [1, 'bar', mocker.Mock(),
        mocker.Mock(),
        timedelta(hours=2)])

    begin = mocker.Mock()
    end = mocker.Mock()
    parse.side_effect = (begin, end)

    tt.cli.main(options)

    calls = [tt.cli.DEFAULT_REPORT_START, tt.cli.DEFAULT_REPORT_END]
    if len(options) == 5:
        calls = [options[2], options[4]]
    elif len(options) == 3:
        if options[1] == '--begin':
            calls[0] = options[2]
        else:
            calls[1] = options[2]

    parse.assert_has_calls(
        [mock.call(ts, settings=tt.cli.DATEPARSER_SETTINGS) for ts in calls])

    timer_service.records.assert_called_with(
        range_begin=begin.replace(), range_end=end.replace())


def test_report(timer_service):
    options = ['report']

    timer_service.report.return_value = [(['foo', 'bar', 'baz', 'bam'], [
        ['1', '2', '3', '4'],
        ['5', '6', '7', '8'],
    ])]

    tt.cli.main(options)
    assert timer_service.report.called


@pytest.mark.parametrize('month', range(1, 13))
def test_report_with_month(month, timer_service):
    options = ['report', '--month', str(month)]

    timer_service.report.return_value = [(['foo', 'bar', 'baz', 'bam'], [
        ['1', '2', '3', '4'],
        ['5', '6', '7', '8'],
    ])]

    tt.cli.main(options)

    today = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0)
    if month > today.month:
        today = today.replace(year=today.year - 1)
    last_day_of_month = calendar.monthrange(today.year, month)[1]

    expected_begin = today.replace(day=1, month=month)
    expected_end = today.replace(day=last_day_of_month, month=month)

    timer_service.report.assert_called_with(
        range_begin=expected_begin, range_end=expected_end)


@pytest.mark.parametrize('destination', ['-', '/tmp/foo'])
@mock.patch('tt.cli.open')
@mock.patch('tt.io.dump')
def test_export(dump, mock_open, destination):
    options = ['export', destination]
    mock_open.return_value = mock.MagicMock(spec=io.IOBase)

    tt.cli.main(options)

    if destination == '-':
        assert not mock_open.called
    else:
        mock_open.assert_called_once_with(destination, 'w')

    assert dump.called


@pytest.mark.parametrize('source', ['-', '/tmp/foo'])
@mock.patch('tt.cli.open')
@mock.patch('tt.io.load')
def test_import(load, mock_open, source):
    options = ['import', source]
    mock_open.return_value = mock.MagicMock(spec=io.IOBase)

    tt.cli.main(options)

    if source == '-':
        assert not mock_open.called
    else:
        mock_open.assert_called_once_with(source, 'r')

    assert load.called


@mock.patch('dateparser.parse')
def test_parse_timestamp(parse, mocker):
    timestamp = mocker.Mock()

    parse.return_value = timestamp

    tt.cli._parse_timestamp('foo')
    parse.assert_called_with('foo', settings=tt.cli.DATEPARSER_SETTINGS)

    timestamp.replace.assert_called_with(microsecond=0)


@mock.patch('dateparser.parse')
def test_parse_timestamp_raises_error(parse):
    parse.return_value = None
    with pytest.raises(ParseError):
        tt.cli._parse_timestamp('foo')
