# Copyright (C) 2018, Anthony Oteri
# All rights reserved.

from datetime import datetime, timedelta
import logging

from tt.exc import ValidationError
import tt.datetime
import tt.task
import tt.timer

log = logging.getLogger(__name__)


class TaskService(object):
    def add(self, name):
        log.debug("Add new task named %s", name)
        tt.task.create(name=name)

    def remove(self, name):
        log.debug("Removing task named %s", name)
        tt.task.remove(name=name)

    def list(self):
        log.debug("Fetching task list")

        for task in tt.task.tasks():
            yield task.name


class TimerService(object):
    def start(self, task, timestamp=datetime.utcnow()):
        log.debug("Starting new timer for %s at %s", task, timestamp)
        tt.timer.create(task=task, start=timestamp)

    def stop(self, timestamp=datetime.utcnow()):
        log.debug("Stopping last active timer at %s", timestamp)
        last = tt.timer.active()
        if last is not None:
            tt.timer.update(last.id, stop=timestamp)

    def summary(self, range_begin=None, range_end=None):
        for task, elapsed in tt.timer.groups_by_timerange(
                start=range_begin, end=range_end):
            yield task, elapsed

    def records(self, range_begin=None, range_end=None):
        for id, task, start, stop, elapsed in tt.timer.timers_by_timerange(
                start=range_begin, end=range_end):
            yield id, task, start, stop, elapsed

    def report(self, range_begin=None, range_end=None):
        period_start, _ = tt.datetime.week_boundaries(range_begin)
        _, period_end = tt.datetime.week_boundaries(range_end)

        for week_start in tt.datetime.range_weeks(period_start, period_end):
            week_end = week_start + timedelta(days=7)
            weekly_data = tt.timer.aggregate_by_task_date(
                start=week_start, end=week_end)

            headers = ['task name'] + list(
                str(d.date())
                for d in tt.datetime.range_weekdays(week_start, week_end))
            rows = []
            for task in weekly_data:
                log.debug('Columns for task %s %s', task,
                          list(weekly_data[task].keys()))
                cols = [task] + [
                    weekly_data[task].get(d.date())
                    for d in tt.datetime.range_weekdays(week_start, week_end)
                ]
                rows.append(cols)

            yield headers, rows
