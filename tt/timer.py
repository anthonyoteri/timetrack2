# Copyright (C) 2018, Anthony Oteri
# All rights reserved.

from datetime import datetime
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

        timer = Timer(task=task, start=start)
        session.add(timer)


def update(id, task=None, start=None, stop=None):
    def validate(timer):
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

            validate(timer)

        except AssertionError as err:
            raise ValidationError("Invalid timer %s: %s" % (timer, err))


def remove(id):
    with transaction() as session:
        session.query(Timer).filter(Timer.id == id).delete()


def timers():
    with transaction() as session:
        for timer in session.query(Timer).all():
            yield timer
