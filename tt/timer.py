# Copyright (C) 2018, Anthony Oteri
# All rights reserved.

import collections
from datetime import datetime, timedelta, timezone
import logging

from sqlalchemy.orm.exc import NoResultFound

from tt.datetime import local_time
from tt.exc import ValidationError
from tt.orm import Task, Timer
from tt.sql import transaction

log = logging.getLogger(__name__)


def create(task, start):
    """Create a new timer for the given task.

    :param str: task: The name of an existing task.
    :param datetime.datetime start: The UTC starting time.
    :raises: ValidationError If the timer fails to validate.
    """

    with transaction() as session:
        try:
            task = session.query(Task).filter(Task.name == task).one()
        except NoResultFound:
            raise ValidationError("Invalid task %s" % task)

        for active in session.query(Timer).filter(Timer.stop.is_(None)).all():
            active.stop = start

        try:
            timer = Timer(task=task, start=start)
            _validate(timer)
            session.add(timer)
        except AssertionError as err:
            raise ValidationError(err)


def update(id, task=None, start=None, stop=None):
    """
    Update one or more fields of a given timer.

    :param id: The ID of the existing timer.
    :param task:  The new task name. (Default value = None)
    :param start:  The new start time. (Default value = None)
    :param stop:  The new stop time. (Default value = None)
    :raises: ValidationError if the timer fails validation checks.
    """
    with transaction() as session:
        try:
            timer = session.query(Timer).get(id)

            if task is not None:
                try:
                    task = session.query(Task).filter(Task.name == task).one()
                except NoResultFound:
                    raise ValidationError("No such task %s" % task)
                timer.task = task

            if start is not None:
                timer.start = start

            if stop is not None:
                timer.stop = stop

            _validate(timer)

        except AssertionError as err:
            raise ValidationError("Invalid timer %s: %s" % (timer, err))


def _validate(timer):
    """Validate time constraints on a timer.

    The following conditions must hold true:

        * The start time must be in the past
        * If there is a stop time, it must be in the past
        * If there is a stop time, the start time must come first

    :param timer:  The timer to validate.
    :raises: AssertionError if the validation conditions are not met.
    """

    now = datetime.now(timezone.utc)
    if timer.running:
        assert timer.start < now, "Start time in the future"
    else:
        assert timer.start < timer.stop, "Start time after stop time"
        assert timer.stop <= now, "Stop time in the future"


def remove(id):
    """
    Remove an existing timer.

    :param id: The id of the timer to delete.
    """
    with transaction() as session:
        session.query(Timer).filter(Timer.id == id).delete()


def active():
    """Fetch the active timer if there is one, or None if not."""
    with transaction() as session:
        return session.query(Timer).filter(Timer.stop.is_(None)).one_or_none()


def timers():
    """Generator for iterating over all timers."""
    with transaction() as session:
        for timer in session.query(Timer).all():
            yield timer


def timers_by_timerange(start, end=datetime.now(timezone.utc)):
    """
    Generate a list of timers which fall between the given start and end
    dates.

    :param start: The datetime.datetime representing the start of the
                  timerange (inclusive)
    :param end:  The datetime.datetime representing the end of the
                 timerange (exclusive)
                 (Default value = datetime.now(timezone.utc)
    :yields: A tuple of (id, task, start, stop, elapsed) for each timer
             which falls within the given timerange.
    """
    with transaction() as session:
        for timer in session.query(Timer).filter(start < Timer.start,
                                                 Timer.start <= end).all():
            yield (timer.id, timer.task.name, timer.start, timer.stop,
                   timer.elapsed)


def groups_by_timerange(start, end=datetime.now(timezone.utc)):
    """
    Construct a summary for the timers within the given timerange.

    :param start: The datetime.datetime representing the start of the
                  timerange (inclusive)
    :param end:  The datetime.datetime representing the end of the
                 timerange (exclusive)
                 (Default value = datetime.now(timezone.utc)
    :yields: A tuple of (task, elapsed) for each task in the given
             timerange.
    """

    with transaction() as session:

        tasks = [
            t[0]
            for t in session.query(Timer.task_id).filter(
                start < Timer.start, Timer.start <= end).distinct(
                    Timer.task_id).order_by(Timer.task_id).all()
        ]

        for task_id in tasks:
            timers = session.query(Timer).filter(
                start < Timer.start, Timer.start <= end,
                Timer.task_id == task_id).all()
            task_name = timers[0].task.name
            elapsed = timedelta(
                seconds=sum(t.elapsed.total_seconds() for t in timers))
            yield task_name, elapsed


def aggregate_by_task_date(start, end):
    """
    Fetch data about tasks per day in a given timerange.

    An example return object is as follows:

    {"task1": {date(2018, 2, 1): timedelta()},
     "task2": {date(2018, 2, 1): timedelta()}}

    :param start: The datetime.datetime representing the start of the
                  timerange. (inclusive)
    :param end: The datetime.datetime representing the end of the timerange
                (exclusive)

    :returns: A nested dictionary of tasks containing the total elapsed time
              spent per day.
    """
    data = collections.defaultdict(lambda: collections.defaultdict(timedelta))

    with transaction() as session:
        for timer in session.query(Timer).filter(start < Timer.start,
                                                 Timer.start <= end).all():
            data[timer.task.name][local_time(
                timer.start).date()] += timer.elapsed

    return data
