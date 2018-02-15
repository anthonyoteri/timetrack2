# Copyright (C) 2018, Anthony Oteri
# All rights reserved

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
    for ts in pandas.date_range(start, end, freq='W-SUN'):
        yield ts.to_pydatetime()


def week_boundaries(date):
    """
    Given a datetime.date object, return the boundaries of the week containing
    that date.  Weeks start on Sunday and end on Saturday.

    :param date: A datetime.date object
    :returns: A tuple of datetime.datetime objects representing the start
              and end of the week containing the given date.
    """
    begin = date - pandas.offsets.Week(weekday=6)
    end = date + pandas.offsets.Week(weekday=5)
    return begin.to_pydatetime(), end.to_pydatetime()


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
