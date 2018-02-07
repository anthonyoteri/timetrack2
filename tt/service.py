# Copyright (C) 2018, Anthony Oteri
# All rights reserved.

from datetime import datetime
import logging

from tt.exc import ValidationError
import tt.task
import tt.timer

log = logging.getLogger(__name__)


class TaskService(object):
    def add(self, name):
        log.debug("Add new task named %s", name)

        try:
            tt.task.create(name=name)
        except ValidationError as err:
            log.error("Error createing task %s: %s", name, err)
            raise

    def remove(self, name):
        log.debug("Removing task named %s", name)

        try:
            tt.task.remove(name=name)
        except ValidationError as err:
            log.error("Error removing task %s: %s", name, err)
            raise

    def list(self):
        log.debug("Fetching task list")

        for task in tt.task.tasks():
            yield task.name


class TimerService(object):
    def start(self, task, timestamp=datetime.utcnow()):
        log.debug("Starting new timer for %s at %s", task, timestamp)

        try:
            tt.timer.create(task=task, start=timestamp)
        except ValidationError as err:
            log.error("Failed to start timer for task %s at %s: %s", task,
                      timestamp, err)
            raise

    def stop(self, timestamp=datetime.utcnow()):
        log.debug("Stopping last active timer at %s", timestamp)

        last = tt.timer.active()
        if last is not None:
            tt.timer.update(last.id, stop=timestamp)

    def summary(self, range_begin=None, range_end=None):
        for task, elapsed in tt.timer.groups_by_timerange(
                start=range_begin, end=range_end):
            yield task, elapsed

    def records(self, range_begin=None, range_end=None):
        for id, task, start, stop, elapsed in tt.timer.timers_by_timerange(
                start=range_begin, end=range_end):
            yield id, task, start, stop, elapsed
