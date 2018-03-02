# Coypright (C) 2018, Anthony Oteri
# All rights reserved

from datetime import datetime, timedelta
from unittest import mock

from dateutil import tz
import pandas
import pytest

import tt.datetime


def test_range_days():
    start = datetime(1970, 1, 1)
    end = datetime(1971, 1, 1)

    expected = list(ts.to_pydatetime() for ts in pandas.date_range(start, end))
    actual = list(tt.datetime.range_days(start, end))

    assert expected == actual


def test_range_weekdays():
    start = datetime(1970, 1, 1)
    end = datetime(1971, 1, 1)

    expected = list(
        ts.to_pydatetime() for ts in pandas.bdate_range(start, end))
    actual = list(tt.datetime.range_weekdays(start, end))

    assert expected == actual


def test_range_weeks():
    start = datetime(1970, 1, 1)
    end = datetime(1971, 1, 1)

    expected = list(ts.to_pydatetime()
                    for ts in pandas.date_range(start, end, freq='W-MON'))
    actual = list(tt.datetime.range_weeks(start, end))

    assert expected == actual


@pytest.mark.parametrize('samples', [
    (datetime(2018, 2, 11), datetime(2018, 2, 5), datetime(2018, 2, 12)),
    (datetime(2018, 2, 12), datetime(2018, 2, 12), datetime(2018, 2, 19)),
    (datetime(2018, 2, 13), datetime(2018, 2, 12), datetime(2018, 2, 19)),
    (datetime(2018, 2, 14), datetime(2018, 2, 12), datetime(2018, 2, 19)),
    (datetime(2018, 2, 15), datetime(2018, 2, 12), datetime(2018, 2, 19)),
    (datetime(2018, 2, 16), datetime(2018, 2, 12), datetime(2018, 2, 19)),
    (datetime(2018, 2, 17), datetime(2018, 2, 12), datetime(2018, 2, 19)),
    (datetime(2018, 2, 18), datetime(2018, 2, 12), datetime(2018, 2, 19)),
    (datetime(2018, 2, 19), datetime(2018, 2, 19), datetime(2018, 2, 26)),
])
def test_week_boundaries(samples):
    date, expected_begin, expected_end = samples
    assert tt.datetime.week_boundaries(date) == (expected_begin, expected_end)


def test_local_time():

    # Validate conversion of naive datetime to aware datetime
    t0 = datetime(2018, 1, 1)
    t1 = tt.datetime.local_time(t0)
    assert t1 == t0.replace(tzinfo=tz.tzutc()).astimezone(tz.tzlocal())

    # Validate conversion of aware datetime to aware datetime
    t2 = tt.datetime.local_time(t0.replace(tzinfo=tz.tzutc()))
    assert t2 == t1

    # Ensure all datetimes represent the same unix timestamp
    epoch = datetime(1970, 1, 1, tzinfo=tz.tzutc())
    assert t2 - epoch == t1 - epoch
    assert t1 - epoch == t0.replace(tzinfo=tz.tzutc()) - epoch


def test_local_time_is_none():
    assert tt.datetime.local_time(None) is None


def test_utc_time():

    # Validate conversion of naive datetime to aware datetime
    t0 = datetime(2018, 1, 1)
    t1 = tt.datetime.utc_time(t0)
    assert t1 == t0.replace(tzinfo=tz.tzlocal()).astimezone(tz.tzutc())

    # Validate conversion of aware datetime to aware datetime
    t2 = tt.datetime.utc_time(t0.replace(tzinfo=tz.tzlocal()))
    assert t2 == t1

    # Ensure all datetimes represent the same unix timestamp
    epoch = datetime(1970, 1, 1, tzinfo=tz.tzutc())
    assert t2 - epoch == t1 - epoch
    assert t1 - epoch == t0.replace(tzinfo=tz.tzlocal()) - epoch


def test_utc_time_is_none():
    assert tt.datetime.utc_time(None) is None


def test_timedelta_to_string():
    td = timedelta(hours=25, minutes=37, seconds=15)
    assert tt.datetime.timedelta_to_string(td) == "25:37"


def test_timedelta_to_string_zero_padding():
    td = timedelta(hours=5, minutes=4, seconds=15)
    assert tt.datetime.timedelta_to_string(td) == "05:04"


def test_start_of_day():
    t = datetime.now(tz.tzlocal())

    expected = t.replace(hour=0, minute=0, second=0, microsecond=0)
    actual = tt.datetime.start_of_day(t)
    assert expected == actual


@mock.patch('tt.datetime.datetime')
def test_start_of_day_no_param(mock_dt):
    t = datetime.now(tz.tzlocal())

    mock_dt.now.return_value = t
    expected = t.replace(hour=0, minute=0, second=0, microsecond=0)
    actual = tt.datetime.start_of_day()

    assert expected == actual


def test_start_of_week():
    t = datetime.now(tz.tzlocal())

    expected = (t - timedelta(days=t.weekday())).replace(
        hour=0, minute=0, second=0, microsecond=0)
    actual = tt.datetime.start_of_week(t)

    assert expected == actual


@mock.patch('tt.datetime.datetime')
def test_start_of_week_no_param(mock_dt):
    t = datetime.now(tz.tzlocal())

    mock_dt.now.return_value = t

    expected = (t - timedelta(days=t.weekday())).replace(
        hour=0, minute=0, second=0, microsecond=0)
    actual = tt.datetime.start_of_week()

    assert expected == actual


def test_start_of_month():
    t = datetime.now(tz.tzlocal())

    expected = t.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    actual = tt.datetime.start_of_month(t)

    assert expected == actual


@mock.patch('tt.datetime.datetime')
def test_start_of_month_no_param(mock_dt):
    t = datetime.now(tz.tzlocal())

    mock_dt.now.return_value = t

    expected = t.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    actual = tt.datetime.start_of_month()

    assert expected == actual


def test_start_of_year():
    t = datetime.now(tz.tzlocal())

    expected = t.replace(
        month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    actual = tt.datetime.start_of_year(t)

    assert expected == actual


@mock.patch('tt.datetime.datetime')
def test_start_of_year_no_param(mock_dt):
    t = datetime.now(tz.tzlocal())

    mock_dt.now.return_value = t

    expected = t.replace(
        month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    actual = tt.datetime.start_of_year()

    assert expected == actual
