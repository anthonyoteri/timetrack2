# Copyright (C) 2018, Anthony Oteri
# All rights reserved.

from datetime import datetime, timezone
import logging

from sqlalchemy.orm.exc import NoResultFound

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
                if stop == '':
                    timer.stop = None
                else:
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


def last():
    """Fetch the last timer, active or not.

    :return dict: The dictionary represenation of the timer or None
    """
    with transaction() as session:
        result = session.query(Timer).order_by(Timer.start.desc()).first()

        return result.as_dict() if result else None


def timers():
    """Generator for iterating over all timers."""
    with transaction() as session:
        for timer in session.query(Timer).all():
            yield timer


def slice(start, end):
    with transaction() as session:
        for timer in session.query(Timer).filter(start <= Timer.start,
                                                 Timer.start < end).all():
            yield timer.as_dict()
