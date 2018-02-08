# Coypright (C) 2018, Anthony Oteri
# All rights reserved

from datetime import date, datetime

import tt.datetime


def test_weekdays():
    weekends = [6, 7, 13, 14]
    expected = [
        datetime(2018, 1, i) for i in range(1, 15) if i not in weekends
    ]

    actual = list(
        tt.datetime.days(
            datetime(2018, 1, 1), datetime(2018, 1, 14), weekdays=True))

    assert expected == actual


def test_weekdays_tuples():
    weekends = [6, 7, 13, 14]

    expected_starts = [
        datetime(2018, 1, i) for i in range(1, 15) if i not in weekends
    ]
    expected_ends = [
        datetime(2018, 1, i) for i in range(2, 16) if i - 1 not in weekends
    ]

    expected = list(zip(expected_starts, expected_ends))

    actual = list(
        tt.datetime.days(
            datetime(2018, 1, 1),
            datetime(2018, 1, 14),
            weekdays=True,
            tuples=True))

    assert expected == actual


def test_days():
    expected = [datetime(2018, 1, i) for i in range(1, 15)]

    actual = list(
        tt.datetime.days(
            datetime(2018, 1, 1, 0, 0, 0), datetime(2018, 1, 14, 23, 59, 59)))

    assert expected == actual


def test_days_tuples():
    expected_starts = [datetime(2018, 1, i) for i in range(1, 15)]
    expected_ends = [datetime(2018, 1, i) for i in range(2, 16)]

    expected = list(zip(expected_starts, expected_ends))

    actual = list(
        tt.datetime.days(
            datetime(2018, 1, 1), datetime(2018, 1, 14), tuples=True))

    assert expected == actual


def test_weeks():
    expected = [
        datetime(2018, 1, 7),
        datetime(2018, 1, 14),
        datetime(2018, 1, 21),
        datetime(2018, 1, 28),
    ]

    actual = list(
        tt.datetime.weeks(datetime(2018, 1, 1), datetime(2018, 2, 1)))

    assert expected == actual


def test_weeks_tuples():
    expected = [
        (datetime(2018, 1, 7), datetime(2018, 1, 14)),
        (datetime(2018, 1, 14), datetime(2018, 1, 21)),
        (datetime(2018, 1, 21), datetime(2018, 1, 28)),
        (datetime(2018, 1, 28), datetime(2018, 2, 4)),
    ]

    actual = list(
        tt.datetime.weeks(
            datetime(2018, 1, 1), datetime(2018, 2, 1), tuples=True))

    assert expected == actual
