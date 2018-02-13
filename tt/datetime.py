# Copyright (C) 2018, Anthony Oteri
# All rights reserved

import pandas

from dateutil import tz


def range_days(start, end):
    for ts in pandas.date_range(start, end):
        yield ts.to_pydatetime()


def range_weekdays(start, end):
    for ts in pandas.bdate_range(start, end):
        yield ts.to_pydatetime()


def range_weeks(start, end):
    for ts in pandas.date_range(start, end, freq='W-SUN'):
        yield ts.to_pydatetime()


def week_boundaries(date):
    begin = date - pandas.offsets.Week(weekday=6)
    end = date + pandas.offsets.Week(weekday=5)
    return begin.to_pydatetime(), end.to_pydatetime()


def local_time(dt):
    return dt.replace(tzinfo=tz.tzutc()).astimezone(tz.tzlocal())


def utc_time(dt):
    return dt.replace(tzinfo=tz.tzlocal()).astimezone(tz.tzutc())
