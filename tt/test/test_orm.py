# Copyright (C) 2018, Anthony Oteri
# All rights reserved

from datetime import datetime

from tt.orm import Task, Timer


def test_task_not_equals():
    task1 = Task(name='foo')
    task2 = Task(name='bar')

    assert task1 != task2


def test_task_equals():
    task = Task(name='foo')

    assert task == task
    assert task is task


def test_task_str():
    task = Task(name='foo')
    assert str(task) == '<Task[name="foo"]>'


def test_task_repr():
    task = Task(name='foo')
    assert repr(task) == '<Task[name="\'foo\'"]>'


def test_timer_not_equals(mocker):
    task1 = Task(name='foo')
    task2 = Task(name='bar')

    ts1 = mocker.MagicMock(spec=datetime)
    ts2 = mocker.MagicMock(spec=datetime)
    timer1 = Timer(task=task1, start=ts1, stop=None)
    timer2 = Timer(task=task2, start=ts2, stop=None)

    assert timer1 != timer2


def test_timer_equals(mocker):
    task = Task(name='foo')
    ts = mocker.MagicMock(spec=datetime)
    timer1 = Timer(task=task, start=ts, stop=None)
    timer2 = Timer(task=task, start=ts, stop=None)

    assert timer1 == timer2


def test_equals_different_types(mocker):
    task = Task(name='foo')
    ts = mocker.MagicMock(spec=datetime)
    timer = Timer(task=task, start=ts, stop=None)

    assert task != timer
