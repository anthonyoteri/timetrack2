# Copyright (C) 2018, Anthony Oteri.
# All rights reserved

from datetime import datetime

import pytest

from tt.exc import ValidationError
from tt.task import create, list as list_, remove
from tt.orm import Task, Timer


def test_create(session):
    create(name='foo')

    results = session.query(Task).filter(Task.name == 'foo').all()
    assert len(results) == 1
    assert results[0].name == 'foo'


def test_create_duplicate_name_raises(session):
    create(name='foo')

    result = session.query(Task).filter(Task.name == 'foo').one()
    assert result.name == 'foo'
    assert result.id == 1

    with pytest.raises(ValidationError):
        create(name='foo')


@pytest.mark.parametrize('name', [None, ''])
def test_create_invalid_name_raises(session, name):
    with pytest.raises(ValidationError):
        create(name=name)


def test_remove(session):
    names = ['foo', 'bar', 'baz', 'boom']
    session.add_all([Task(name=n) for n in names])
    session.flush()

    before_count = session.query(Task).count()

    remove(name='bar')

    assert session.query(Task).count() == before_count - 1

    for name in set(names) - set(['bar']):
        assert session.query(Task).filter(Task.name == name).count() == 1


@pytest.mark.parametrize('name', ['buzz', None, ''])
def test_remove_invalid_task_raises(session, name):

    session.add_all([
        Task(name='foo'),
        Task(name='bar'),
        Task(name='baz'),
        Task(name='boom'),
    ])
    session.flush()

    with pytest.raises(ValidationError):
        remove(name=name)


def test_remove_task_with_timers_raises(session):

    session.add(Task(name='foo'))
    session.flush()

    task = session.query(Task).get(1)

    session.add(Timer(task=task, start=datetime.utcnow()))
    session.flush()

    timer = session.query(Timer).get(1)

    # Ensure that there is a valid 2-way relationship
    assert timer in task.timers
    assert timer.task == task

    with pytest.raises(ValidationError):
        remove('foo')


@pytest.mark.skip(reason='No way of currently testing this')
def test_list(session):

    names = ['foo', 'bar', 'baz', 'boom']
    session.add_all([Task(name=n) for n in names])
    session.flush()

    list_()

    # TODO: Refactor list function and complete this test.
