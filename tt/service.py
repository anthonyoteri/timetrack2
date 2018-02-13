# Copyright (C) 2018, Anthony Oteri
# All rights reserved.

from datetime import datetime, timedelta, timezone
import logging

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

    def rename(self, old_name, new_name):
        log.debug("Renaming %s to %s", old_name, new_name)
        task = tt.task.get(name=old_name)
        tt.task.update(task.id, name=new_name)

    def list(self):
        log.debug("Fetching task list")

        for task in tt.task.tasks():
            yield task.name


class TimerService(object):
    def start(self, task, timestamp=datetime.now(timezone.utc)):
        log.debug("Starting new timer for %s at %s", task, timestamp)
        tt.timer.create(task=task, start=timestamp)

    def stop(self, timestamp=datetime.now(timezone.utc)):
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

    def report(self, range_begin=None, range_end=None, threshold=15 * 60):
        period_start, _ = tt.datetime.week_boundaries(range_begin)
        _, period_end = tt.datetime.week_boundaries(range_end)

        for week_start in tt.datetime.range_weeks(period_start, period_end):
            week_end = week_start + timedelta(days=7)
            weekly_data = tt.timer.aggregate_by_task_date(
                start=range_begin, end=range_end)

            dates = [
                str(d.date())
                for d in tt.datetime.range_weekdays(week_start, week_end)
            ]
            headers = ['task name'] + dates + ['Total']
            rows = []
            for task in weekly_data:
                log.debug('Columns for task %s %s', task,
                          list(weekly_data[task].keys()))
                cols = [
                    weekly_data[task].get(d.date())
                    for d in tt.datetime.range_weekdays(week_start, week_end)
                ]
                total = timedelta(
                    seconds=sum(c.total_seconds() for c in cols
                                if c is not None) or 0)
                if total >= timedelta(seconds=threshold):
                    rows.append([task] + cols + [total])

            totals = [
                timedelta(
                    seconds=sum([
                        c.total_seconds() for c in r
                        if isinstance(c, timedelta)
                    ]) or 0) for r in zip(*rows)
            ][1:]
            totals = totals or [timedelta(0)] * 7

            log.debug("len totals %d, totals %s", len(totals), totals)

            rows.append(['TOTAL'] + totals)
            yield headers, rows
