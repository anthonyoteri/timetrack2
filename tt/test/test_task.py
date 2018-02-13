# Copyright (C) 2018, Anthony Oteri.
# All rights reserved

from datetime import datetime, timezone

import pytest

from tt.exc import ValidationError
from tt.task import create, get, update, remove, tasks
from tt.orm import Task, Timer


def test_create(session):
    create(name='foo')

    results = session.query(Task).filter(Task.name == 'foo').all()
    assert len(results) == 1
    assert results[0].name == 'foo'
    assert results[0].description is None


def test_create_with_description(session):
    create(name='foo', description="Foobar")

    results = session.query(Task).filter(Task.name == 'foo').all()
    assert len(results) == 1
    assert results[0].name == 'foo'
    assert results[0].description == 'Foobar'


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


def test_get_task(session):
    create(name='foo')
    task = get(name='foo')
    assert task.id == 1
    assert task.name == 'foo'


def test_rename_task(session):
    create(name='foo')

    update(1, name='bar')

    task = session.query(Task).get(1)
    assert task.name == 'bar'


def test_rename_duplicate_name_raises(session):
    create(name='foo')
    create(name='bar')

    with pytest.raises(ValidationError):
        update(2, name='foo')


def test_describe_task(session):
    create(name='foo', description='old')
    update(1, description='bar')

    task = session.query(Task).get(1)
    assert task.name == 'foo'
    assert task.description == 'bar'


def test_describe_task_blank_erases(session):
    create(name='foo', description='foobar')
    update(1, description='')

    task = session.query(Task).get(1)
    assert task.name == 'foo'
    assert task.description is None


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

    session.add(Timer(task=task, start=datetime.now(timezone.utc)))
    session.flush()

    timer = session.query(Timer).get(1)

    # Ensure that there is a valid 2-way relationship
    assert timer in task.timers
    assert timer.task == task

    with pytest.raises(ValidationError):
        remove('foo')


def test_all(session):

    names = ['foo', 'bar', 'baz', 'boom']
    session.add_all([Task(name=n) for n in names])

    for expected_name, task in zip(names, tasks()):
        assert task.name == expected_name
