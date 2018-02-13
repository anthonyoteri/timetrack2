# Coypright (C) 2018, Anthony Oteri
# All rights reserved

from datetime import datetime

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
                    for ts in pandas.date_range(start, end, freq='W-SUN'))
    actual = list(tt.datetime.range_weeks(start, end))

    assert expected == actual


@pytest.mark.parametrize('samples', [
    (datetime(2014, 7, 23), datetime(2014, 7, 20), datetime(2014, 7, 26)),
    (datetime(2014, 6, 10), datetime(2014, 6, 8), datetime(2014, 6, 14)),
    (datetime(2018, 2, 8), datetime(2018, 2, 4), datetime(2018, 2, 10)),
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
