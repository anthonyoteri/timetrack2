# Copyright (C) 2018, Anthony Oteri.
# All rights reserved

import pytest

from tt.task import create, list as list_, remove
from tt.orm import Task


def test_create(session):
    create(name='foo')

    results = session.query(Task).filter(Task.name == 'foo').all()
    assert len(results) == 1
    assert results[0].name == 'foo'


def test_create_duplicate_name_is_rejected(session):
    create(name='foo')

    result = session.query(Task).filter(Task.name == 'foo').one()
    assert result.name == 'foo'
    assert result.id == 1

    create(name='foo')

    results = session.query(Task).filter(Task.name == 'foo').all()
    assert len(results) == 1
    assert results[0].name == 'foo'
    assert results[0].id == 1


@pytest.mark.parametrize('name', [None, ''])
def test_create_invalid_name_is_rejected(session, name):
    create(name=name)
    assert session.query(Task).count() == 0


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
def test_remove_invalid_task_is_rejected(session, name):

    session.add_all([
        Task(name='foo'),
        Task(name='bar'),
        Task(name='baz'),
        Task(name='boom'),
    ])
    session.flush()

    before_count = session.query(Task).count()

    remove(name=name)

    assert session.query(Task).count() == before_count


@pytest.mark.skip(reason='No way of currently testing this')
def test_list(session):

    names = ['foo', 'bar', 'baz', 'boom']
    session.add_all([Task(name=n) for n in names])
    session.flush()

    list_()

    # TODO: Refactor list function and complete this test.
