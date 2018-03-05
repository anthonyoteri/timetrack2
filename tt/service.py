# Copyright (C) 2018, Anthony Oteri
# All rights reserved.

import collections
from datetime import datetime, timedelta, timezone
import logging

from sqlalchemy.orm.exc import NoResultFound

from tt.exc import BadRequest, ValidationError
from tt.datatable import Datatable
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
        try:
            tt.task.remove(name=name)
        except ValidationError as err:
            raise BadRequest(err)

    def rename(self, old_name, new_name):
        """
        Rename an existing task.

        :param old_name: An existing task name
        :param new_name: The new name

        """
        log.debug("Renaming %s to %s", old_name, new_name)
        try:
            task = tt.task.get(name=old_name)
        except NoResultFound:
            raise BadRequest("Unable to locate task with name %s" % old_name)

        tt.task.update(task.id, name=new_name)

    def describe(self, name, description):
        """
        Update the long description for an existing task.

        :param name: The name of the task.
        :param description:  The new description
        """
        log.debug("Adding description to task %s: %s", name, description)
        try:
            task = tt.task.get(name=name)
        except NoResultFound:
            raise BadRequest("Unable to locate task with name %s" % name)

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
        if task is None:
            last = tt.timer.last()
            if last is not None:
                log.debug("Resuming last task")
                task = last['task']
            else:
                raise BadRequest("No task to resume")

        log.debug("Starting new timer for %s at %s", task, timestamp)
        try:
            tt.timer.create(task=task, start=timestamp)
        except ValidationError as err:
            raise BadRequest(err)

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
        else:
            raise BadRequest("No running task to stop")

    def update(self, id, task=None, start=None, stop=None):
        """
        Update an existing timer.

        :param id: The ID of the existing timer.
        :param task: The new task name.
        :param start: The new start time.
        :param stop: The new stop time or empty string to clear.
        """
        log.debug("Updating existing timer with id %s", id)
        try:
            tt.timer.update(id=id, task=task, start=start, stop=stop)
        except ValidationError as err:
            raise BadRequest(err)

    def delete(self, id):
        """
        Delete a timer by ID.

        :param id: The ID of the existing timer.
        """
        log.debug("Deleting existing timer with id %s", id)
        tt.timer.remove(id=id)

    def slice_grouped_by_date(self, start=None, end=None, elapsed=False):
        """Group a selection of records by date

        :param start: The starting date (inclusive)
        :param end: The ending date (exclusive)
        :param elapsed: If True, return the total elapsed time per bucket.
                        If False, return the list of matching timers per
                        bucket.
        :yields: A tuple of Date, and either a list of records or the total
                 elapsed time.
        """

        start = start or datetime(1970, 1, 1, tzinfo=timezone.utc)
        end = end or datetime.now(tt.datetime.tz_local())

        timers = tt.timer.slice(start=start, end=end)

        results = collections.defaultdict(list)
        for timer in timers:
            key = timer['start'].date()
            results[key].append(timer)

        for k, v in results.items():
            if elapsed:
                yield k, timedelta(
                    seconds=sum([t['elapsed'].total_seconds() for t in v]))
            else:
                yield k, v

    def slice_grouped_by_task(self, start=None, end=None, elapsed=False):
        """Group a selection of records by task

        :param start: The starting date (inclusive)
        :param end: The ending date (exclusive)
        :param elapsed: If True, return the total elapsed time per bucket.
                        If False, return the list of matching timers per
                        bucket.
        :yields: A tuple of task name, and either a list of records or the
                 total elapsed time.
        """
        start = start or datetime(1970, 1, 1, tzinfo=timezone.utc)
        end = end or datetime.now(tt.datetime.tz_local())

        timers = tt.timer.slice(start=start, end=end)

        results = collections.defaultdict(list)
        for timer in timers:
            key = timer['task']
            results[key].append(timer)

        for k, v in results.items():
            if elapsed:
                yield k, timedelta(
                    seconds=sum([t['elapsed'].total_seconds() for t in v]))
            else:
                yield k, v

    def slice_grouped_by_date_task(self, start=None, end=None, elapsed=False):
        """Group a selection of records by date and task

        :param start: The starting date (inclusive)
        :param end: The ending date (exclusive)
        :param elapsed: If True, return the total elapsed time per bucket.
                        If False, return the list of matching timers per
                        bucket.
        :yields: A tuple of date, task name, and either a list of records or
                 the total elapsed time.
        """
        start = start or datetime(1970, 1, 1, tzinfo=timezone.utc)
        end = end or datetime.now(tt.datetime.tz_local())

        timers = tt.timer.slice(start=start, end=end)

        results = collections.defaultdict(
            lambda: collections.defaultdict(list))
        for timer in timers:
            date_key = timer['start'].date()
            task_key = timer['task']
            results[date_key][task_key].append(timer)

        for date_key, tasks in results.items():
            for task_key, v in tasks.items():
                if elapsed:
                    yield date_key, task_key, timedelta(
                        seconds=sum([t['elapsed'].total_seconds() for t in v]))
                else:
                    yield date_key, task_key, v


class ReportingService(object):
    def __init__(self, timer_service):
        self.timer_service = timer_service
        Datatable.table_fmt = "fancy_grid"
        Datatable.value_fn = self._formatter

    def timers_by_day(self, start, end):
        for day, timers in self.timer_service.slice_grouped_by_date(
                start=start, end=end):
            columns = ['id', 'task', 'start', 'stop', 'elapsed']
            table = Datatable(table=timers, headers=columns)
            table.caption = day.strftime('%A %B %d, %Y')
            yield table

    def summary_by_task(self, start, end):
        columns = ['elapsed']
        table = Datatable(headers=columns)

        total = timedelta(0)
        for task, elapsed in self.timer_service.slice_grouped_by_task(
                start=start, end=end, elapsed=True):
            table.append({'elapsed': elapsed}, label=task)
            total += elapsed
        table.append({"elapsed": total}, label='TOTAL')

        return table

    def summary_by_day_and_task(self, start, end):
        extended_start, _ = tt.datetime.week_boundaries(start)

        for week_start in tt.datetime.range_weeks(extended_start, end):

            if week_start == end:
                break

            week_end = week_start + timedelta(days=7)

            slice_ = list(
                self.timer_service.slice_grouped_by_date_task(
                    start=week_start, end=week_end, elapsed=True))

            if not slice_:
                continue

            sheet = collections.defaultdict(dict)
            task_totals = collections.defaultdict(timedelta)
            day_totals = collections.defaultdict(timedelta)

            for date_key, task_key, elapsed in slice_:
                sheet[task_key][date_key] = elapsed
                task_totals[task_key] += elapsed
                day_totals[date_key] += elapsed

            table = Datatable(
                header_fn=lambda x: x.strftime('%a %b %d'),
                label_header=' ' * 16,
                summary_header='Total')
            for t in sheet:
                row = {k: v for k, v in sheet[t].items()}
                table.append(
                    row,
                    label=t,
                    summary=tt.datetime.timedelta_to_string(task_totals[t]))
            total_time = timedelta(
                seconds=sum([t.total_seconds() for t in day_totals.values()]))
            table.append(
                day_totals,
                label="TOTAL",
                summary=tt.datetime.timedelta_to_string(total_time))

            table.caption = 'Week %s' % week_start.strftime('%W')

            yield table

    def _formatter(self, value):
        if isinstance(value, datetime):
            return tt.datetime.local_time(value).replace(tzinfo=None)
        if isinstance(value, timedelta):
            return tt.datetime.timedelta_to_string(value)
        return value
