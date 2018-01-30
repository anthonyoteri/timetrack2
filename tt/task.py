# Copyright (C) 2018, Anthony Oteri
# All rights reserved




import logging

from sqlalchemy import Column, Integer, String
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship
from sqlalchemy.orm.exc import NoResultFound

from tt.db import Base, transaction, transactional

log = logging.getLogger(__name__)


class Task(Base):
    __tablename__ = 'task'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)

    timers = relationship("Timer", back_populates="task")
    records = relationship("TimeRecord", back_populates="task")

    def __repr__(self):
        return "<Task(id={}, name={})>".format(self.id, self.name)


def create(name):
    log.debug('creating task with name %s', name)

    try:
        with transaction() as session:
            task = Task(name=name)
            session.add(task)
    except IntegrityError as err:
        log.warning("A task with name %s already exists" % name)
        return


@transactional
def list(session):
    log.debug('listing tasks')

    print("All tasks:")
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
                log.error('task %s has %d active timers' % (task.name, len(task.timers)))
                return
    except IntegrityError:
        log.error("Can not remove a task with existing records")
        return

