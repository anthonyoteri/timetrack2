# Copyright (C) 2018, Anthony Oteri
# All rights reserved.

import collections
from datetime import datetime
import logging

import humanfriendly
import dateparser
from sqlalchemy import Column, DateTime, ForeignKey, Integer
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

from tt.db import Base, transaction, transactional
from tt.exc import TimerLimitExceeded
from tt.task import Task

log = logging.getLogger(__name__)

ACTIVE_TIMER_LIMIT = 1
DATEPARSER_SETTINGS = {'TO_TIMEZONE': 'UTC', 'RETURN_AS_TIMEZONE_AWARE': False}


class Timer(Base):
    __tablename__ = 'timer'
    id = Column(Integer, primary_key=True)
    start_time = Column(DateTime)
    task_id = Column(
        Integer, ForeignKey('task.id'), nullable=False, unique=True)

    task = relationship("Task", back_populates="timers")

    def __repr__(self):
        return '<Timer(id=%s, task=%s, start_time=%s)>' % (self.id, self.task,
                                                           self.start_time)


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

            _enforce_active_timer_limit(session)

            task = session.query(Task).filter(Task.name == task).one()
            timestamp = timestamp.replace(microsecond=0)

            timer = Timer(task=task, start_time=timestamp)
            session.add(timer)
    except IntegrityError:
        log.error('A timer for this task is already running')
        return


def _enforce_active_timer_limit(session):
    active_count = session.query(Timer).count()
    if active_count >= ACTIVE_TIMER_LIMIT:
        raise TimerLimitExceeded("Too many running timers %d, limit %d" %
                                 (active_count, ACTIVE_TIMER_LIMIT))


def _find_timer_by_id_or_task(session, id_or_task):
    try:
        timer = session.query(Timer).get(int(id_or_task))
    except ValueError:
        try:
            task = session.query(Task).filter(Task.name == id_or_task).one()
        except NoResultFound:
            log.error("Invalid task %s" % id_or_task)
            return None
        try:
            timer = session.query(Timer).filter(Timer.task == task).one()
        except MultipleResultsFound:
            log.warn('Multiple timers found for task %s, use id instead',
                     id_or_task)
            return None
        except NoResultFound:
            log.warn('No timer found with task %s', id_or_task)
            return None

    return timer


@transactional
def stop(session, t, timestamp):
    timer = _find_timer_by_id_or_task(session, t)
    if timer is None:
        log.error("Timer not found")
        return

    timestamp = timestamp.replace(microsecond=0)

    record = TimeRecord(
        task=timer.task, start_time=timer.start_time, stop_time=timestamp)
    session.add(record)
    session.delete(timer)


@transactional
def cancel(session, t):
    timer = _find_timer_by_id_or_task(session, t)
    if timer is None:
        log.error("Timer not found")
        return

    session.delete(timer)


@transactional
def update_task(session, t, value):
    timer = _find_timer_by_id_or_task(session, t)
    if timer is None:
        log.error("Timer not found")
        return

    try:
        task = session.query(Task).filter(Task.name == value).one()
    except NoResultFound:
        log.error('Invalid task %s' % value)
        return

    timer.task = task


@transactional
def update_start(session, t, value):
    timer = _find_timer_by_id_or_task(session, t)
    if timer is None:
        log.error("Timer not found")
        return

    timestamp = dateparser.parse(
        value, settings=DATEPARSER_SETTINGS).replace(microsecond=0)

    if timestamp > datetime.utcnow():
        log.error("Cannot change start time in the future")
        return

    timer.start_time = timestamp


@transactional
def timers(session):

    format_string = "| %4s | %15s | %19s | %29s |"

    print('+' + "-" * 78 + '+')
    print(format_string % ("ID", "TASK", "START TIME", "ELAPSED"))
    print('+' + "=" * 78 + '+')
    for timer in session.query(Timer).all():
        elapsed = datetime.utcnow().replace(microsecond=0) - timer.start_time
        print(format_string %
              (timer.id, timer.task.name, timer.start_time,
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
        print(format_string %
              (record.id, record.task.name, record.start_time,
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
    for task, elapsed in summary.items():
        print(format_string % (task, humanfriendly.format_timespan(elapsed)))
    print('+' + "-" * 78 + '+')

    print(format_string %
          ('TOTAL', humanfriendly.format_timespan(sum(summary.values()))))

    print('+' + "-" * 78 + '+')
