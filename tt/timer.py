# Copyright (C) 2018, Anthony Oteri
# All rights reserved.

import collections
from datetime import datetime, timedelta
import logging

from sqlalchemy.orm.exc import NoResultFound

from tt.exc import ValidationError
from tt.orm import Task, Timer
from tt.sql import transaction

log = logging.getLogger(__name__)


def create(task, start):
    """Creat a timer for the given task.

    :param str task: The name of an existing task.
    :param datetime.datetime start: The start time.
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

    Raises AssertionError: If any of the above conditions are not met.
    """

    now = datetime.utcnow()
    if timer.running:
        assert timer.start < now, "Start time in the future"
    else:
        assert timer.start < timer.stop, "Start time after stop time"
        assert timer.stop <= now, "Stop time in the future"


def remove(id):
    with transaction() as session:
        session.query(Timer).filter(Timer.id == id).delete()


def active():
    with transaction() as session:
        return session.query(Timer).filter(Timer.stop.is_(None)).one_or_none()


def timers():
    with transaction() as session:
        for timer in session.query(Timer).all():
            yield timer


def timers_by_timerange(start, end=datetime.utcnow()):
    with transaction() as session:
        for timer in session.query(Timer).filter(start < Timer.start,
                                                 Timer.start <= end).all():
            yield (timer.id, timer.task.name, timer.start, timer.stop,
                   timer.elapsed)


def groups_by_timerange(start, end=datetime.utcnow()):

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

    data = collections.defaultdict(lambda: collections.defaultdict(timedelta))

    with transaction() as session:
        for timer in session.query(Timer).filter(start < Timer.start,
                                                 Timer.start <= end).all():
            data[timer.task.name][timer.start.date()] += timer.elapsed

    return data
