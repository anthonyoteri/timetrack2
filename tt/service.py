# Copyright (C) 2018, Anthony Oteri
# All rights reserved.

from datetime import datetime, timedelta, timezone
import logging

import tt.datetime
import tt.task
import tt.timer

log = logging.getLogger(__name__)


class TaskService(object):
    def add(self, name, description=None):
        """
        Add a new task.

        :param name: The task name.
        :param description:  An optional description.
        """
        log.debug("Add new task named %s", name)
        tt.task.create(name=name, description=description)

    def remove(self, name):
        """
        Remove a task by name.

        :param name: The name of the existing task to remove.
        """
        log.debug("Removing task named %s", name)
        tt.task.remove(name=name)

    def rename(self, old_name, new_name):
        """
        Rename an existing task.

        :param old_name: An existing task name
        :param new_name: The new name

        """
        log.debug("Renaming %s to %s", old_name, new_name)
        task = tt.task.get(name=old_name)
        tt.task.update(task.id, name=new_name)

    def describe(self, name, description):
        """
        Update the long description for an existing task.

        :param name: The name of the task.
        :param description:  The new description
        """
        log.debug("Adding description to task %s: %s", name, description)
        task = tt.task.get(name=name)
        tt.task.update(task.id, description=description)

    def list(self):
        """
        List all tasks:

        :yields: Tuples of (name, description) for each task.
        """
        log.debug("Fetching task list")

        for task in tt.task.tasks():
            yield task.name, task.description


class TimerService(object):
    def start(self, task, timestamp=datetime.now(timezone.utc)):
        """
        Start a timer.

        :param task: The name of an existing task.
        :param timestamp:  The timezone-aware start time.
                           (Default value = datetime.now(timezone.utc)
        """
        log.debug("Starting new timer for %s at %s", task, timestamp)
        tt.timer.create(task=task, start=timestamp)

    def stop(self, timestamp=datetime.now(timezone.utc)):
        """
        Stop the active timer.

        :param timestamp:  The timezone-aware stop time.
                           (Default value = datetime.now(timezone.utc)
        """
        log.debug("Stopping last active timer at %s", timestamp)
        last = tt.timer.active()
        if last is not None:
            tt.timer.update(last.id, stop=timestamp)

    def update(self, id, task=None, start=None, stop=None):
        """
        Update an existing timer.

        :param id: The ID of the existing timer.
        :param task: The new task name.
        :param start: The new start time.
        :param stop: The new stop time or empty string to clear.
        """
        log.debug("Updating existing timer with id %s", id)
        tt.timer.update(id=id, task=task, start=start, stop=stop)

    def delete(self, id):
        """
        Delete a timer by ID.

        :param id: The ID of the existing timer.
        """
        log.debug("Deleting existing timer with id %s", id)
        tt.timer.remove(id=id)

    def summary(self, range_begin=None, range_end=None):
        """
        Report the task and total elapsed time for each task within
        the given timerange.

        :param range_begin: The timezone-aware start time (inclusive)
        :param range_end:  The timezone-aware end time (exclusive)
        :yields: A tuple of (task, elapsed) for each task.
        """
        total = timedelta(0)
        for task, elapsed in tt.timer.groups_by_timerange(
                start=range_begin, end=range_end):
            total += elapsed
            yield task, elapsed
        yield "TOTAL", total

    def records(self, range_begin=None, range_end=None):
        """
        Report each timer within the given timerange.

        :param range_begin:  The timezone-aware start time (inclusive)
        :param range_end:  The timezone-aware end time (exclusive)

        :yields A tuple of (id, task, start, stop, elapsed) for each timer.
        """
        for id, task, start, stop, elapsed in tt.timer.timers_by_timerange(
                start=range_begin, end=range_end):
            yield id, task, start, stop, elapsed

    def report(self, range_begin=None, range_end=None, threshold=15 * 60):
        """
        Generate weekly tables for full weeks covering the given timerange.

        If the given range_begin or range_end do not fall on week boundaries,
        The reported tables will contain any days outside of the given range
        to make completed weeks.  E.g. if the range_begin falls on a
        Tuesday, the table will include the previous Monday, however no data
        will be shown in days outside of the given range.

        Each table will be yeilded as a list of lists, where the first column
        in each row will contain the name of the task, and the last column will
        represent the total time spent during that week on that task.  For
        example:

        [['task1', timedelta(...), None, None, None, None, timedelta(...)],
         ['task2', None, timedelta(...), None, None, None, timedelta(...)]]

        Additionally, the list of header columns will be yielded. E.g.

        ['Task', '02-01', '02-02', ..., 'Total']

        :param range_begin:  The start date for records (inclusive)
        :param range_end:  The end date for records (exclusive)
        :param threshold:  The minimum number of seconds, under wich values
                           will not be reported.(Default value = 15 * 60)

        :yields Tuples of (headers, table_data) for each week.
        """
        period_start, _ = tt.datetime.week_boundaries(range_begin)
        _, period_end = tt.datetime.week_boundaries(range_end)

        for week_start in tt.datetime.range_weeks(period_start, period_end):
            _, week_end = tt.datetime.week_boundaries(week_start)
            weekly_data = tt.timer.aggregate_by_task_date(
                start=range_begin, end=range_end)

            dates = [
                d.date().strftime('%b %d')
                for d in tt.datetime.range_weekdays(week_start, week_end)
            ]
            headers = [" " * 16] + dates + ['Total']
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
                    ]) or 0) or None for r in zip(*rows)
            ][1:]
            totals = totals or [None] * 6

            log.debug("len totals %d, totals %s", len(totals), totals)

            rows.append(['TOTAL'] + totals)
            yield headers, rows
