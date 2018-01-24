# Copyright (C) 2018, Anthony Oteri
# All rights reserved.

from __future__ import absolute_import, division, print_function

import collections
from datetime import datetime
import logging

import humanfriendly
from sqlalchemy import Column, DateTime, ForeignKey, Integer
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

from tt.db import Base, transaction, transactional
from tt.task import Task


log = logging.getLogger(__name__)


class Timer(Base):
    __tablename__ = 'timer'
    id = Column(Integer, primary_key=True)
    start_time = Column(DateTime)
    task_id = Column(Integer,
                     ForeignKey('task.id'),
                     nullable=False,
                     unique=True)

    task = relationship("Task", back_populates="timers")

    def __repr__(self):
        return '<Timer(id=%s, task=%s, start_time=%s)>' % (
                self.id, self.task, self.start_time)


class TimeRecord(Base):
    __tablename__ = 'time_record'
    id = Column(Integer, primary_key=True)
    start_time = Column(DateTime, nullable=False)
    stop_time = Column(DateTime, nullable=False)

    task_id = Column(Integer, ForeignKey('task.id'), nullable=False)
    task = relationship("Task", back_populates="records")

    def __repr__(self):
        return '<TimeRecord(id=%s, task=%s, start_time=%s, stop_time=%s)>' % (
                self.id, self.task, self.start_time, self.stop_time)


def start(task, timestamp):
    try:
        with transaction() as session:
            task = session.query(Task).filter(Task.name == task).one()

            timestamp = timestamp.replace(microsecond=0)

            timer = Timer(task=task, start_time=timestamp)
            session.add(timer)
    except IntegrityError:
        log.error('A timer for this task is already running')
        return


@transactional
def stop(session, t, timestamp):

    try:
        timer = session.query(Timer).get(int(t))
    except ValueError:
        task = session.query(Task).filter(Task.name == t).one()
        try:
            timer = session.query(Timer).filter(Timer.task == task).one()
        except MultipleResultsFound:
            log.warn('Multiple timers found for task %s, use id instead', t)
            return
        except NoResultFound:
            log.warn('No timer found with task %s', t)
            return

    timestamp = timestamp.replace(microsecond=0)

    record = TimeRecord(task=timer.task,
                        start_time=timer.start_time,
                        stop_time=timestamp)
    session.add(record)
    session.delete(timer)


@transactional
def timers(session):

    format_string = "| %4s | %15s | %19s | %29s |"

    print('+' + "-" * 78 + '+')
    print(format_string % ("ID", "TASK", "START TIME", "ELAPSED"))
    print('+' + "=" * 78 + '+')
    for timer in session.query(Timer).all():
        elapsed = datetime.utcnow().replace(microsecond=0) - timer.start_time
        print(format_string % (
            timer.id, timer.task.name, timer.start_time,
            humanfriendly.format_timespan(elapsed.total_seconds())))

    print('+' + "-" * 78 + '+')


@transactional
def history(session):
    format_string = "| %4s | %15s | %19s | %29s |"

    print('+' + "-" * 78 + '+')
    print(format_string % ("ID", "TASK", "START TIME", "TOTAL"))
    print('+' + "=" * 78 + '+')
    for record in session.query(TimeRecord).all():
        total = record.stop_time - record.start_time
        print(format_string % (
            record.id, record.task.name, record.start_time,
            humanfriendly.format_timespan(total.total_seconds())))

    print('+' + "-" * 78 + '+')


@transactional
def summarize(session):

    summary = collections.defaultdict(int)
    for record in session.query(TimeRecord).all():
        elapsed = record.stop_time - record.start_time
        summary[record.task.name] += elapsed.total_seconds()

    format_string = "| %22s | %51s |"
    print('+' + "-" * 78 + '+')
    print(format_string % ("TASK", "TOTAL"))
    print('+' + "=" * 78 + '+')
    for task, elapsed in summary.iteritems():
        print(format_string % (task, humanfriendly.format_timespan(elapsed)))
    print('+' + "-" * 78 + '+')

    print (format_string % ('TOTAL', humanfriendly.format_timespan(sum(summary.values()))))
    print('+' + "-" * 78 + '+')


         
