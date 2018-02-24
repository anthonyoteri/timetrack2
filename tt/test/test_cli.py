# Copyright (C) 2017, Anthony Oteri
# All rights reserved.

import calendar
from datetime import datetime, timedelta
import logging
import io
from unittest import mock

import pytest

import tt
import tt.cli
from tt.datetime import tz_local, start_of_day
from tt.exc import ParseError


@pytest.fixture
def task_service(mocker):
    init = mocker.patch('tt.cli.TaskService')
    service = mocker.MagicMock()
    init.return_value = service
    return service


@pytest.fixture
def timer_service(mocker):
    init = mocker.patch('tt.cli.TimerService')
    service = mocker.MagicMock()
    init.return_value = service
    return service


@mock.patch('tt.cli.print')
def test_version(mock_print):
    tt.cli.main(['--version'])
    mock_print.assert_called_with('Timetrack2-%s' % tt.__VERSION__)


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
    ['create', 'foo', 'bar'],
])
def test_create(options, task_service):
    tt.cli.main(options)

    if len(options) == 2:
        task_service.add.assert_called_with(name=options[1], description=None)
    else:
        task_service.add.assert_called_with(
            name=options[1], description=options[2])


def test_describe(task_service):
    options = ['describe', 'foo', 'bar']
    tt.cli.main(options)
    task_service.describe.assert_called_with(name='foo', description='bar')


def test_rename(task_service):
    options = ['rename', 'foo', 'bar']
    tt.cli.main(options)
    task_service.rename.assert_called_with(old_name='foo', new_name='bar')


@pytest.mark.parametrize('options', [
    ['tasks'],
])
def test_tasks(options, mocker, task_service):
    task_service.list.return_value = iter([('foo', 'one'), ('bar', 'two'),
                                           ('bam', 'three')])
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

    timestamp = mocker.MagicMock(spec=datetime)
    parse.return_value = timestamp

    tt.cli.main(options)

    if len(options) == 3:
        parse.assert_called_with(
            options[2], settings=tt.cli.DATEPARSER_SETTINGS)
    else:
        parse.assert_called_with('now', settings=tt.cli.DATEPARSER_SETTINGS)

    timer_service.start.assert_called_with(
        task=options[1], timestamp=timestamp.replace().replace().astimezone())


@pytest.mark.parametrize('options', [['stop', 'now'], ['stop']])
@mock.patch('dateparser.parse')
def test_stop(parse, options, mocker, timer_service):

    timestamp = mocker.MagicMock(spec=datetime)
    parse.return_value = timestamp

    tt.cli.main(options)

    if len(options) == 2:
        parse.assert_called_with(
            options[1], settings=tt.cli.DATEPARSER_SETTINGS)
    else:
        parse.assert_called_with('now', settings=tt.cli.DATEPARSER_SETTINGS)

    timer_service.stop.assert_called_with(
        timestamp=timestamp.replace().replace().astimezone())


@mock.patch('tt.cli.datetime', spec=datetime)
@mock.patch('tt.cli.isinstance')
def test_summary(mock_isinstance, mock_datetime, mocker, timer_service):
    timer_service.summary.return_value = (['foo', timedelta(hours=1)],
                                          ['bar', timedelta(hours=2)])

    t0 = start_of_day(datetime.now(tz_local()))
    t1 = t0 + timedelta(days=1)

    mock_isinstance.return_value = False
    mock_datetime.now.return_value = t0

    tt.cli.main(['summary'])

    timer_service.summary.assert_called_once_with(range_begin=t0, range_end=t1)


def test_summary_begin_end(mocker, timer_service):
    timer_service.summary.return_value = (['foo', timedelta(hours=1)],
                                          ['bar', timedelta(hours=2)])

    t0 = datetime.now(tz_local()).replace(microsecond=0) - timedelta(hours=4)
    t1 = t0 + timedelta(hours=3)

    tt.cli.main(
        ['summary', '--begin',
         t0.isoformat(), '--end',
         t1.isoformat()])

    timer_service.summary.assert_called_once_with(range_begin=t0, range_end=t1)


@mock.patch('tt.cli.datetime', spec=datetime)
@mock.patch('tt.cli.isinstance')
def test_records(mock_isinstance, mock_datetime, mocker, timer_service):
    timer_service.records.return_value = ([
        1, 'foo',
        mocker.MagicMock(spec=datetime),
        mocker.MagicMock(spec=datetime),
        timedelta(hours=1)
    ], [
        1, 'bar',
        mocker.MagicMock(spec=datetime),
        mocker.MagicMock(spec=datetime),
        timedelta(hours=2)
    ])

    t0 = start_of_day(datetime.now(tz_local()))
    t1 = t0 + timedelta(days=1)

    mock_isinstance.return_value = False
    mock_datetime.now.return_value = t0

    tt.cli.main(['records'])

    timer_service.records.assert_called_once_with(range_begin=t0, range_end=t1)


def test_records_begin_end(mocker, timer_service):
    timer_service.records.return_value = ([
        1, 'foo',
        mocker.MagicMock(spec=datetime),
        mocker.MagicMock(spec=datetime),
        timedelta(hours=1)
    ], [
        1, 'bar',
        mocker.MagicMock(spec=datetime),
        mocker.MagicMock(spec=datetime),
        timedelta(hours=2)
    ])

    t0 = datetime.now(tz_local()).replace(microsecond=0) - timedelta(hours=4)
    t1 = t0 + timedelta(hours=3)

    tt.cli.main(
        ['records', '--begin',
         t0.isoformat(), '--end',
         t1.isoformat()])

    timer_service.records.assert_called_once_with(range_begin=t0, range_end=t1)


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

    today = datetime.now(tz_local()).replace(
        hour=0, minute=0, second=0, microsecond=0)
    if month > today.month:
        today = today.replace(year=today.year - 1)
    last_day_of_month = calendar.monthrange(today.year, month)[1]

    expected_begin = today.replace(day=1, month=month)
    expected_end = today.replace(day=last_day_of_month, month=month)

    timer_service.report.assert_called_with(
        range_begin=expected_begin, range_end=expected_end)


@mock.patch('tt.cli.datetime', autospec=datetime)
@mock.patch('tt.cli.isinstance')
def test_status(mock_isinstance, mock_datetime, mocker, timer_service):
    options = ['status']
    mock_isinstance.return_value = False
    timer_service.report.return_value = [(['foo', 'bar', 'baz', 'bam'], [
        ['1', '2', '3', '4'],
        ['5', '6', '7', '8'],
    ])]
    timer_service.records.return_value = [[
        1, 'foo',
        mocker.MagicMock(spec=datetime),
        mocker.MagicMock(spec=datetime),
        timedelta(hours=1)
    ]]

    mock_datetime.now.return_value = datetime(2018, 2, 19)

    tt.cli.main(options)
    timer_service.report.assert_called_with(
        range_begin=datetime(2018, 2, 19), range_end=datetime(2018, 2, 25))

    timer_service.records.assert_called_with(
        range_begin=datetime(2018, 2, 19), range_end=datetime(2018, 2, 20))


@pytest.mark.parametrize('destination', ['-', '/tmp/foo'])
@mock.patch('tt.cli.open')
@mock.patch('tt.io.dump')
@mock.patch('sys.stdout')
def test_export(stdout, dump, mock_open, destination):
    options = ['export', destination]

    out = mock.MagicMock(spec=io.IOBase)
    mock_open.return_value = out

    tt.cli.main(options)

    if destination != '-':
        mock_open.assert_called_once_with(destination, 'w')
        dump.assert_called_once_with(mock.ANY, out.__enter__.return_value)
    else:
        dump.assert_called_once_with(mock.ANY, stdout)


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
    timestamp = mocker.MagicMock(spec=datetime)

    parse.return_value = timestamp

    tt.cli._parse_timestamp('foo')
    parse.assert_called_with('foo', settings=tt.cli.DATEPARSER_SETTINGS)

    timestamp.replace.assert_called_with(microsecond=0)


@mock.patch('dateparser.parse')
def test_parse_timestamp_raises_error(parse):
    parse.return_value = None
    with pytest.raises(ParseError):
        tt.cli._parse_timestamp('foo')


@mock.patch('tt.cli.datetime')
def test_from_timerange(mock_datetime, mocker):
    t = datetime(2018, 2, 23, 15, 16, 00, tzinfo=tz_local())

    mock_datetime.now.return_value = t

    args = mocker.MagicMock()
    args.yesterday = False
    args.week = False
    args.last_week = False
    args.month = False
    args.last_month = False
    args.year = False
    args.last_year = False

    assert tt.cli.from_timerange(args) == (datetime(
        2018, 2, 23, 0, 0, tzinfo=tz_local()),
                                           datetime(
                                               2018,
                                               2,
                                               24,
                                               0,
                                               0,
                                               tzinfo=tz_local()))


@mock.patch('tt.cli.datetime')
def test_from_timerange_yesterday(mock_datetime, mocker):
    t = datetime(2018, 2, 23, 15, 16, 00, tzinfo=tz_local())

    mock_datetime.now.return_value = t

    args = mocker.MagicMock()
    args.yesterday = True
    args.week = False
    args.last_week = False
    args.month = False
    args.last_month = False
    args.year = False
    args.last_year = False

    assert tt.cli.from_timerange(args) == (datetime(
        2018, 2, 22, 0, 0, tzinfo=tz_local()),
                                           datetime(
                                               2018,
                                               2,
                                               23,
                                               0,
                                               0,
                                               tzinfo=tz_local()))


@mock.patch('tt.cli.datetime')
def test_from_timerange_week(mock_datetime, mocker):
    t = datetime(2018, 2, 23, 15, 16, 00, tzinfo=tz_local())

    mock_datetime.now.return_value = t

    args = mocker.MagicMock()
    args.yesterday = False
    args.week = True
    args.last_week = False
    args.month = False
    args.last_month = False
    args.year = False
    args.last_year = False

    assert tt.cli.from_timerange(args) == (datetime(
        2018, 2, 19, 0, 0, tzinfo=tz_local()),
                                           datetime(
                                               2018,
                                               2,
                                               26,
                                               0,
                                               0,
                                               tzinfo=tz_local()))


@mock.patch('tt.cli.datetime')
def test_from_timerange_last_week(mock_datetime, mocker):
    t = datetime(2018, 2, 23, 15, 16, 00, tzinfo=tz_local())

    mock_datetime.now.return_value = t

    args = mocker.MagicMock()
    args.yesterday = False
    args.week = False
    args.last_week = True
    args.month = False
    args.last_month = False
    args.year = False
    args.last_year = False

    assert tt.cli.from_timerange(args) == (datetime(
        2018, 2, 12, 0, 0, tzinfo=tz_local()),
                                           datetime(
                                               2018,
                                               2,
                                               19,
                                               0,
                                               0,
                                               tzinfo=tz_local()))


@mock.patch('tt.cli.datetime')
def test_from_timerange_month(mock_datetime, mocker):
    t = datetime(2018, 2, 23, 15, 16, 00, tzinfo=tz_local())

    mock_datetime.now.return_value = t

    args = mocker.MagicMock()
    args.yesterday = False
    args.week = False
    args.last_week = False
    args.month = True
    args.last_month = False
    args.year = False
    args.last_year = False

    assert tt.cli.from_timerange(args) == (datetime(
        2018, 2, 1, 0, 0, tzinfo=tz_local()),
                                           datetime(
                                               2018,
                                               3,
                                               1,
                                               0,
                                               0,
                                               tzinfo=tz_local()))


@mock.patch('tt.cli.datetime')
def test_from_timerange_last_month(mock_datetime, mocker):
    t = datetime(2018, 2, 23, 15, 16, 00, tzinfo=tz_local())

    mock_datetime.now.return_value = t

    args = mocker.MagicMock()
    args.yesterday = False
    args.week = False
    args.last_week = False
    args.month = False
    args.last_month = True
    args.year = False
    args.last_year = False

    assert tt.cli.from_timerange(args) == (datetime(
        2018, 1, 1, 0, 0, tzinfo=tz_local()),
                                           datetime(
                                               2018,
                                               2,
                                               1,
                                               0,
                                               0,
                                               tzinfo=tz_local()))


@mock.patch('tt.cli.datetime')
def test_from_timerange_year(mock_datetime, mocker):
    t = datetime(2018, 2, 23, 15, 16, 00, tzinfo=tz_local())

    mock_datetime.now.return_value = t

    args = mocker.MagicMock()
    args.yesterday = False
    args.week = False
    args.last_week = False
    args.month = False
    args.last_month = False
    args.year = True
    args.last_year = False

    assert tt.cli.from_timerange(args) == (datetime(
        2018, 1, 1, 0, 0, tzinfo=tz_local()),
                                           datetime(
                                               2019,
                                               1,
                                               1,
                                               0,
                                               0,
                                               tzinfo=tz_local()))


@mock.patch('tt.cli.datetime')
def test_from_timetrange_last_year(mock_datetime, mocker):
    t = datetime(2018, 2, 23, 15, 16, 00, tzinfo=tz_local())

    mock_datetime.now.return_value = t

    args = mocker.MagicMock()
    args.yesterday = False
    args.week = False
    args.last_week = False
    args.month = False
    args.last_month = False
    args.year = False
    args.last_year = True

    assert tt.cli.from_timerange(args) == (datetime(
        2017, 1, 1, 0, 0, tzinfo=tz_local()),
                                           datetime(
                                               2018,
                                               1,
                                               1,
                                               0,
                                               0,
                                               tzinfo=tz_local()))


def test_init():
    """Test the module initialization when __main__ module."""
    with mock.patch.object(tt.cli, "main", return_value=42):
        with mock.patch.object(tt.cli, "__name__", "__main__"):
            with mock.patch.object(tt.cli.sys, 'exit') as mock_exit:
                tt.cli.__init__()

                assert mock_exit.call_args[0][0] == 42
