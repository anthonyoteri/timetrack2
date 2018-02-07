# Copyright (C) 2018, Anthony Oteri
# All rights reserved.

from datetime import datetime, timedelta

import pytest

from tt.exc import ValidationError
from tt.timer import (active, create, groups_by_timerange, remove, timers,
                      timers_by_timerange, update, _validate)
from tt.orm import Task, Timer


@pytest.fixture
def task(session):
    return Task(name='foo')


def test_create(session, task):
    session.add(task)

    start = datetime.utcnow() - timedelta(hours=1)
    create(task=task.name, start=start)

    assert session.query(Timer).count() == 1

    timer = session.query(Timer).get(1)
    assert timer.start == start
    assert timer.task.id == task.id
    assert timer.stop is None
    assert timer.elapsed >= timedelta(hours=1)
    assert timer.running


def test_create_start_in_the_future_raises(session, task):
    session.add(task)

    start = datetime.utcnow() + timedelta(hours=1)
    with pytest.raises(ValidationError):
        create(task=task.name, start=start)


def test_create_invalid_task_raises(session):

    assert session.query(Task).filter(Task.name == 'bad').count() == 0
    with pytest.raises(ValidationError):
        create(task="bad", start=datetime.utcnow())


def test_create_second_timer_stops_first(session, task):
    session.add(task)

    now = datetime.utcnow()

    one_hour_ago = now - timedelta(hours=1)
    two_hours_ago = now - timedelta(hours=2)

    create(task=task.name, start=two_hours_ago)
    assert session.query(Timer).count() == 1

    create(task=task.name, start=one_hour_ago)
    assert session.query(Timer).count() == 2

    timer_one = session.query(Timer).get(1)
    timer_two = session.query(Timer).get(2)

    # Make sure we have the correct timers based on their start time.
    assert timer_one.start == two_hours_ago
    assert timer_two.start == one_hour_ago

    assert not timer_one.running
    assert timer_two.running

    assert timer_one.stop == timer_two.start


def test_update_timer_task(session):

    old_task = Task(name='old')
    new_task = Task(name='new')

    session.add_all([old_task, new_task])

    session.add(Timer(task=old_task, start=datetime.utcnow()))

    update(1, task=new_task.name)

    timer = session.query(Timer).get(1)
    assert timer.task.id == new_task.id


def test_update_timer_invalid_task_raises(session, task):
    session.add(task)

    session.add(Timer(task=task, start=datetime.utcnow()))

    with pytest.raises(ValidationError):
        update(1, task='invalid_task_name')


def test_update_time_start(session, task):

    session.add(task)

    now = datetime.utcnow()
    one_hour_ago = now - timedelta(hours=1)
    two_hours_ago = now - timedelta(hours=2)

    session.add(Timer(task=task, start=one_hour_ago))

    update(1, start=two_hours_ago)

    timer = session.query(Timer).get(1)
    assert timer.start == two_hours_ago


@pytest.mark.parametrize(
    'offset',
    [
        timedelta(minutes=-30),  # Start time after stop time
        timedelta(hours=1),  # Start time in the future
    ])
def test_update_invalid_start_raises(session, task, offset):

    session.add(task)

    now = datetime.utcnow()
    one_hour_ago = now - timedelta(hours=1)
    two_hours_ago = now - timedelta(hours=2)
    start_time = now + offset

    session.add(Timer(task=task, start=two_hours_ago, stop=one_hour_ago))

    with pytest.raises(ValidationError):
        update(1, start=start_time)


def test_update_time_stop(session, task):

    session.add(task)

    now = datetime.utcnow()
    one_hour_ago = now - timedelta(hours=1)
    two_hours_ago = now - timedelta(hours=2)

    session.add(Timer(task=task, start=two_hours_ago, stop=one_hour_ago))

    update(1, stop=now)

    timer = session.query(Timer).get(1)
    assert timer.stop == now


@pytest.mark.parametrize(
    'offset',
    [
        timedelta(hours=1),  # Stop time in the future
        timedelta(hours=-2),  # Stop time before start
    ])
def test_update_stop_time_invalid_constraint(session, task, offset):

    session.add(task)

    now = datetime.utcnow()
    an_hour_ago = now - timedelta(hours=1)
    stop_time = now + offset

    session.add(Timer(task=task, start=an_hour_ago, stop=now))

    with pytest.raises(ValidationError):
        update(1, stop=stop_time)


def test_remove(session, task):
    session.add(task)

    session.add(Timer(task=task, start=datetime.utcnow()))

    assert session.query(Timer).count() == 1
    remove(1)

    assert session.query(Timer).count() == 0


def test_active_running(session, task):
    session.add(task)

    session.add(Timer(task=task, start=datetime.utcnow()))

    cur = active()

    assert cur is not None
    assert cur.id == 1


def test_active_stopped(session, task):
    session.add(task)

    session.add(
        Timer(task=task, start=datetime.utcnow(), stop=datetime.utcnow()))

    assert active() is None


def test_timers(session, task):
    session.add(task)

    now = datetime.utcnow()
    duration = timedelta(hours=1)

    for hours in range(100, 0, -1):
        offset = timedelta(hours=hours)
        start = now - offset - duration
        stop = start + duration
        session.add(Timer(task=task, start=start, stop=stop))

    assert session.query(Timer).count() == 100

    timers_ = timers()
    assert len(list(timers_)) == 100


def test_timers_by_timerange(session, task):

    session.add(task)

    now = datetime.utcnow()
    duration = timedelta(hours=1)

    for hours in range(100, 0, -1):
        offset = timedelta(hours=hours)
        start = now - offset - duration
        stop = start + duration
        session.add(Timer(task=task, start=start, stop=stop))

    start = now - timedelta(hours=24)

    assert len(list(timers_by_timerange(start=start, end=now))) == 22

    for (t_id, t_task, t_start, t_stop, t_elapsed) in timers_by_timerange(
            start=start, end=now):
        assert t_start > start
        assert t_start <= now


def test_groups_by_timerange(session):

    session.add(Task(name='even'))
    session.add(Task(name='odd'))

    now = datetime.utcnow()
    duration = timedelta(hours=1)

    for i, hours in enumerate(range(100, 0, -1)):
        offset = timedelta(hours=hours)
        start = now - offset - duration
        stop = start + duration
        task = session.query(Task).get(1 if i % 2 == 0 else 2)
        session.add(Timer(task=task, start=start, stop=stop))

    start = now - timedelta(hours=25)

    expected = [('even', timedelta(hours=11)), ('odd', timedelta(hours=12))]
    assert list(groups_by_timerange(start=start, end=now)) == expected


@pytest.mark.parametrize('running', [False, True])
def test_validate(running):

    start = datetime.utcnow() - timedelta(hours=1)
    stop = start + timedelta(minutes=30)

    t = Timer(start=start, stop=None if running else stop)
    _validate(t)


def test_validate_start_in_future():
    start = datetime.utcnow() + timedelta(hours=1)
    with pytest.raises(AssertionError):
        _validate(Timer(start=start))


def test_validate_stop_before_start():
    start = datetime.utcnow() - timedelta(hours=1)
    stop = start - timedelta(hours=1)

    with pytest.raises(AssertionError):
        _validate(Timer(start=start, stop=stop))


def test_validate_stop_in_future():

    start = datetime.utcnow() - timedelta(hours=1)
    stop = start + timedelta(hours=2)

    with pytest.raises(AssertionError):
        _validate(Timer(start=start, stop=stop))
