# Copyright (C) 2018, Anthony Oteri
# All rights reserved

from datetime import timedelta

import pandas


def days(start, end, weekdays=False, tuples=False):

    func = pandas.bdate_range if weekdays else pandas.date_range

    for timestamp in func(start, end):
        date = timestamp.to_pydatetime()
        if tuples:
            yield date, date + timedelta(days=1)
        else:
            yield date


def weeks(start, end, tuples=False):
    for timestamp in pandas.date_range(start, end, freq='W-SUN'):
        date = timestamp.to_pydatetime()
        if tuples:
            yield date, date + timedelta(days=7)
        else:
            yield date
