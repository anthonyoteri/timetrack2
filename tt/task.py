# Copyright (C) 2018, Anthony Oteri
# All rights reserved

import logging

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from tt.orm import Task
from tt.sql import transaction

log = logging.getLogger(__name__)


def create(name):
    log.debug('creating task with name %s', name)

    if not name:
        log.warning("Invalid task name")
        return

    try:
        with transaction() as session:
            task = Task(name=name)
            session.add(task)
    except IntegrityError:
        log.warning("A task with name %s already exists" % name)
        return


def list():
    log.debug('listing tasks')

    print("All tasks:")
    with transaction() as session:
        for task in session.query(Task).all():
            print("  %s" % task.name)


def remove(name):
    log.debug('remove task with name %s', name)

    try:
        with transaction() as session:
            try:
                task = session.query(Task).filter(Task.name == name).one()
            except NoResultFound:
                log.error('no such task with name %s', name)
                return

            if not task.timers:
                session.delete(task)
            else:
                log.error('task %s has %d active timers' % (task.name,
                                                            len(task.timers)))
                return
    except IntegrityError:
        log.error("Can not remove a task with existing records")
        return
