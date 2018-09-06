# Copyright (C) 2018, Anthony Oteri
# All rights reserved

import logging

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from tt.exc import ValidationError
from tt.orm import Task
from tt.sql import transaction

log = logging.getLogger(__name__)


def create(name, description=None):
    """
    Create a new task.

    :param name: The task name.
    :param description:  An optional description which will be shown when
                         listing tasks.
    :raises: ValidationError If there is a database conflict because a task
             with the given name already exists, or if the name is invalid.
    """
    log.debug("creating task with name %s, description=%s", name, description)

    if name == "":
        raise ValidationError("Cannot use empty name")

    try:
        with transaction() as session:
            task = Task(name=name, description=description)
            session.add(task)
    except IntegrityError:
        raise ValidationError("A task with name %s already exists" % name)


def get(name):
    """
    Get a task record by name.

    :param name: The name of the task.
    :return: A Task record.
    """
    with transaction() as session:
        return session.query(Task).filter(Task.name == name).one()


def update(id, name=None, description=None):
    """
    Update an existing task with the supplied name or desciption.

    The provided name must adhear to the same validation conditions as
    for the create() method.  E.g. it must not be empty, and must not
    already exist. If the empty string is passed as the descripition,
    any existing description will be removed.

    :param id: The ID of an existing task.
    :param name: A new name for the task. (Default value = None)
    :param description:  A new description for the task. (Default value = None)
    :raises: ValidationError If the name already exists on a different task,
             or if the name is invalid.
    """
    log.debug("updating task %s with name=%s", id, name)

    try:
        with transaction() as session:
            task = session.query(Task).get(id)
            if name is not None:
                task.name = name
            if description is not None:
                if description == "":
                    task.description = None
                else:
                    task.description = description
    except IntegrityError:
        raise ValidationError("A task with name %s already exists" % name)


def tasks():
    """Generator for iterating through all tasks."""
    with transaction() as session:
        for task in session.query(Task).all():
            yield task


def remove(name):
    """
    Remove a task by name.

    A task may be removed only if there are no timers, active or stopped,
    using the existing task.

    :param name: The name of an existing task.
    :raises: ValidationError if no task exists with the given name, or if
             there is a problem removing the task.
    """
    log.debug("remove task with name %s", name)

    try:
        with transaction() as session:
            try:
                task = session.query(Task).filter(Task.name == name).one()
            except NoResultFound:
                raise ValidationError("no such task with name %s", name)

            session.delete(task)
    except IntegrityError:
        raise ValidationError("Can not remove a task with existing records")
