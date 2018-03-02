# Copyright (C) 2018, Anthony Oteri
# All rights reserved.

from datetime import date, datetime, timedelta
from unittest import mock

import pytest

from tt.datetime import tz_local
from tt.exc import ValidationError
from tt.orm import Task, Timer
from tt.service import TaskService, TimerService, ReportingService


@pytest.fixture
def task_service():
    return TaskService()


@pytest.fixture
def timer_service():
    return TimerService()


@pytest.fixture
def reporting_service(mocker):
    return ReportingService(mocker.MagicMock(spec=TimerService))


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


@pytest.fixture
def slices():
    return [
        {
            'start': datetime(2018, 2, 28, 9, 0, tzinfo=tz_local()),
            'elapsed': timedelta(hours=1),
            'task': 'one',
        },
        {
            'start': datetime(2018, 2, 28, 10, 0, tzinfo=tz_local()),
            'elapsed': timedelta(hours=2),
            'task': 'two',
        },
        {
            'start': datetime(2018, 2, 28, 11, 0, tzinfo=tz_local()),
            'elapsed': timedelta(hours=4),
            'task': 'one',
        },
        {
            'start': datetime(2018, 3, 1, 9, 0, tzinfo=tz_local()),
            'elapsed': timedelta(hours=8),
            'task': 'two',
        },
        {
            'start': datetime(2018, 3, 1, 10, 0, tzinfo=tz_local()),
            'elapsed': timedelta(hours=16),
            'task': 'one',
        },
        {
            'start': datetime(2018, 3, 1, 11, 0, tzinfo=tz_local()),
            'elapsed': timedelta(hours=32),
            'task': 'two',
        },
    ]


@mock.patch('tt.timer.slice')
def test_slice_grouped_by_date(mocked_slice, slices, timer_service):

    mocked_slice.return_value = slices

    results = list(timer_service.slice_grouped_by_date())

    assert results == [
        (date(2018, 2, 28), slices[:3]),
        (date(2018, 3, 1), slices[3:]),
    ]


@mock.patch('tt.timer.slice')
def test_slice_grouped_by_date_elapsed(mocked_slice, slices, timer_service):

    mocked_slice.return_value = slices

    results = list(timer_service.slice_grouped_by_date(elapsed=True))
    assert results == [
        (date(2018, 2, 28), timedelta(hours=7)),
        (date(2018, 3, 1), timedelta(hours=56)),
    ]


@mock.patch('tt.timer.slice')
def test_slice_grouped_by_task(mocked_slice, slices, timer_service):

    mocked_slice.return_value = slices

    results = list(timer_service.slice_grouped_by_task())
    assert results == [
        ('one', [slices[0], slices[2], slices[4]]),
        ('two', [slices[1], slices[3], slices[5]]),
    ]


@mock.patch('tt.timer.slice')
def test_slice_grouped_by_task_elapsed(mocked_slice, slices, timer_service):

    mocked_slice.return_value = slices

    results = list(timer_service.slice_grouped_by_task(elapsed=True))

    assert results == [
        ('one', timedelta(hours=21)),
        ('two', timedelta(hours=42)),
    ]


@mock.patch('tt.timer.slice')
def test_slice_grouped_by_date_task(mocked_slice, slices, timer_service):

    mocked_slice.return_value = slices

    results = list(timer_service.slice_grouped_by_date_task())

    assert results == [
        (date(2018, 2, 28), 'one', [slices[0], slices[2]]),
        (date(2018, 2, 28), 'two', [slices[1]]),
        (date(2018, 3, 1), 'two', [slices[3], slices[5]]),
        (date(2018, 3, 1), 'one', [slices[4]]),
    ]


@mock.patch('tt.timer.slice')
def test_slice_grouped_by_date_task_elapsed(mocked_slice, slices,
                                            timer_service):

    mocked_slice.return_value = slices

    results = list(timer_service.slice_grouped_by_date_task(elapsed=True))

    assert results == [
        (date(2018, 2, 28), 'one', timedelta(hours=5)),
        (date(2018, 2, 28), 'two', timedelta(hours=2)),
        (date(2018, 3, 1), 'two', timedelta(hours=40)),
        (date(2018, 3, 1), 'one', timedelta(hours=16)),
    ]


def test_timers_by_day(mocker, reporting_service):
    slice_ = [(mocker.MagicMock(spec=date), [mocker.MagicMock(spec=dict)])]
    reporting_service.timer_service.slice_grouped_by_date.return_value = slice_

    start = mocker.MagicMock(spec=datetime)
    end = mocker.MagicMock(spec=datetime)

    tables = list(reporting_service.timers_by_day(start, end))

    assert tables

    reporting_service.timer_service.slice_grouped_by_date\
        .assert_called_once_with(start=start, end=end)


def test_summary_by_task(mocker, reporting_service):
    slice_ = [(mocker.MagicMock(spec=str), mocker.MagicMock(spec=timedelta))]
    reporting_service.timer_service.slice_grouped_by_task.return_value = slice_

    start = mocker.MagicMock(spec=datetime)
    end = mocker.MagicMock(spec=datetime)

    table = reporting_service.summary_by_task(start, end)

    assert table

    reporting_service.timer_service.slice_grouped_by_task\
        .assert_called_once_with(start=start, end=end, elapsed=True)


@mock.patch('tt.datetime.range_weeks')
@mock.patch('tt.datetime.week_boundaries')
def test_summary_by_day_and_task(mock_week_boundaries, mock_range_weeks,
                                 mocker, reporting_service):
    slice_ = [(mocker.MagicMock(spec=datetime), mocker.MagicMock(spec=str),
               timedelta(seconds=600))]
    reporting_service.timer_service.slice_grouped_by_date_task\
        .return_value = slice_

    start = mocker.MagicMock(spec=datetime)
    end = mocker.MagicMock(spec=datetime)

    week_start = mocker.MagicMock(spec=datetime)
    mock_week_boundaries.return_value = (week_start, None)

    mock_range_weeks.return_value = [week_start]

    table = list(reporting_service.summary_by_day_and_task(start, end))
    assert table

    mock_week_boundaries.assert_called_once_with(start)
    mock_range_weeks.assert_called_once_with(week_start, end)
    reporting_service.timer_service.slice_grouped_by_date_task\
        .assert_called_once_with(start=week_start, end=mock.ANY, elapsed=True)


@mock.patch('tt.datetime.range_weeks')
@mock.patch('tt.datetime.week_boundaries')
def test_summary_by_day_and_task_week_start_is_end(
        mock_week_boundaries, mock_range_weeks, mocker, reporting_service):
    slice_ = [(mocker.MagicMock(spec=datetime), mocker.MagicMock(spec=str),
               timedelta(seconds=600))]
    reporting_service.timer_service.slice_grouped_by_date_task\
        .return_value = slice_

    start = mocker.MagicMock(spec=datetime)
    end = mocker.MagicMock(spec=datetime)

    mock_week_boundaries.return_value = (end, None)
    mock_range_weeks.return_value = [end]

    table = list(reporting_service.summary_by_day_and_task(start, end))
    assert not table


@mock.patch('tt.datetime.range_weeks')
@mock.patch('tt.datetime.week_boundaries')
def test_summary_by_day_and_task_no_data(
        mock_week_boundaries, mock_range_weeks, mocker, reporting_service):
    slice_ = []
    reporting_service.timer_service.slice_grouped_by_date_task\
        .return_value = slice_

    start = mocker.MagicMock(spec=datetime)
    end = mocker.MagicMock(spec=datetime)

    week_start = mocker.MagicMock(spec=datetime)
    mock_week_boundaries.return_value = (week_start, None)

    mock_range_weeks.return_value = [week_start]

    table = list(reporting_service.summary_by_day_and_task(start, end))
    assert not table


@pytest.mark.parametrize(
    'value',
    [datetime(1970, 1, 1), timedelta(hours=1), "foo"])
def test_formatter(value, reporting_service):
    assert reporting_service._formatter(value) is not None
