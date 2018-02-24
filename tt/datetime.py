# Copyright (C) 2018, Anthony Oteri
# All rights reserved

from datetime import datetime, timedelta

import pandas

from dateutil import tz


def range_days(start, end):
    """
    Generate a range of datetime.datetime objects between the given start
    and end dates.

    :param start: The starting date, inclusive.
    :param end: The ending date, inclusive.
    :yields: One datetime.datetime object per day between start and end
    """
    for ts in pandas.date_range(start, end):
        yield ts.to_pydatetime()


def range_weekdays(start, end):
    """
    Generate a range of datetime.datetime objects between the given start
    and end dates, skipping weekends.

    :param start: The starting date, inclusive.
    :param end: The ending date, inclusive.
    :yields: One datetime.datetime object per weekday between start and end.
    """
    for ts in pandas.bdate_range(start, end):
        yield ts.to_pydatetime()


def range_weeks(start, end):
    """
    Generate a range of datetime.datetime objects between the given start
    and end dates, representing the first Sunday of each week.

    :param start: The starting date, inclusive.
    :param end: The ending date, inclusive.
    :yields: One datetime.datetime object per week between start and end.
    """
    for ts in pandas.date_range(start, end, freq='W-MON'):
        yield ts.to_pydatetime()


def week_boundaries(date):
    """
    Given a datetime.date object, return the boundaries of the week containing
    that date.  Weeks start on Monday and end on Sunday.

    :param date: A datetime.date object
    :returns: A tuple of datetime.datetime objects representing the start
              and end of the week containing the given date.
    """
    beginning = date - timedelta(days=date.weekday())
    end = beginning + timedelta(days=6)

    # Double-check that weeks are Monday - Sunday
    assert beginning.weekday() == 0
    assert end.weekday() == 6

    return beginning, end


def local_time(dt):
    """
    Convert a datetime.datetime object to a timezone-aware datetime.datetime
    in the users local timezone.

    :param dt: A datetime.datetime object.
    :returns: A timezone-aware datetime.datetime object in the users local
              timezone.
    """
    return dt.replace(tzinfo=tz.tzutc()).astimezone(tz.tzlocal())


def utc_time(dt):
    """
    Convert a datetime.datetime object to a timezone-aware datetime.datetime
    in UTC.

    :param dt: A datetime.datetime object.
    :returns: A timezone-aware datetime.datetime object in UTC.
    """
    return dt.replace(tzinfo=tz.tzlocal()).astimezone(tz.tzutc())


def timedelta_to_string(td):
    """
    Format a timedelta as a string containting "HH:MM".

    :param td: A datetime.timedelta object.
    :returns: A string representing the timedelta in hours:minutes format.
    """
    hours, remainder = divmod(int(td.total_seconds()), 3600)
    minutes, _ = divmod(remainder, 60)
    return "%02d:%02d" % (hours, minutes)


def tz_local():
    """Return the local timezone."""
    return tz.tzlocal()


def start_of_day(dt=None):
    """
    Determine the start of a day.

    :param dt: A datetime.datetime object.
    :returns: The datetime representing the first second of the day.
    """
    if dt is None:
        dt = datetime.now(tz_local())

    return dt.replace(hour=0, minute=0, second=0, microsecond=0)


def start_of_week(dt=None):
    """
    Determine the start of a week.

    :param dt: A datetime.datetime object.
    :returns: The datetime representing the first second of the week.
    """
    if dt is None:
        dt = datetime.now(tz_local())

    start, _ = week_boundaries(dt)
    return start_of_day(start)


def start_of_month(dt=None):
    """
    Determine the start of a month.

    :param dt: A datetime.datetime object.
    :returns: The datetime representing the first second of the month.
    """

    if dt is None:
        dt = datetime.now(tz_local())

    return start_of_day(dt.replace(day=1))


def start_of_year(dt=None):
    """
    Determine the start of a year.

    :param dt: A datetime.datetime object.
    :returns: The datetime representing the first second of January 1.
    """

    if dt is None:
        dt = datetime.now(tz_local())

    return start_of_month(dt.replace(month=1))
