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
    log.debug('creating task with name %s, description=%s', name, description)

    if name == "":
        raise ValidationError("Cannot use empty name")

    try:
        with transaction() as session:
            task = Task(name=name, description=description)
            session.add(task)
    except IntegrityError:
        raise ValidationError("A task with name %s already exists" % name)


def get(name):
    with transaction() as session:
        return session.query(Task).filter(Task.name == name).one()


def update(id, name=None, description=None):
    log.debug('updating task %s with name=%s', id, name)

    try:
        with transaction() as session:
            task = session.query(Task).get(id)
            if name is not None:
                task.name = name
            if description is not None:
                if description == '':
                    task.description = None
                else:
                    task.description = description
    except IntegrityError:
        raise ValidationError("A task with name %s already exists" % name)


def tasks():
    with transaction() as session:
        for task in session.query(Task).all():
            yield task


def remove(name):
    log.debug('remove task with name %s', name)

    try:
        with transaction() as session:
            try:
                task = session.query(Task).filter(Task.name == name).one()
            except NoResultFound:
                raise ValidationError('no such task with name %s', name)

            session.delete(task)
    except IntegrityError:
        raise ValidationError("Can not remove a task with existing records")
