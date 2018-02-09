# Coypright (C) 2018, Anthony Oteri
# All rights reserved

from datetime import datetime

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
