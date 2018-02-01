# Copyright (C) 2018, Anthony Oteri
# All rights reserved.

import logging

import dateparser

from tt.exc import ParseError, ValidationError
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
    def start(self, task, timestamp="now"):
        timestamp = self._parse_timestamp(timestamp)
        log.debug("Starting new timer for %s at %s", task, timestamp)

        try:
            tt.timer.create(task=task, start=timestamp)
        except ValidationError as err:
            log.error("Failed to start timer for task %s at %s: %s", task,
                      timestamp, err)
            raise

    def stop(self, timestamp="now"):
        timestamp = self._parse_timestamp(timestamp)
        log.debug("Stopping last active timer at %s", timestamp)

        last = tt.timer.active()
        if last is not None:
            tt.timer.update(last.id, stop=timestamp)

    def _parse_timestamp(self, timestamp_in):
        timestamp_out = dateparser.parse(
            timestamp_in,
            settings={
                'TO_TIMEZONE': 'UTC',
                'RETURN_AS_TIMEZONE_AWARE': False
            })

        if timestamp_out is None:
            raise ParseError("Unable to parse %s" % timestamp_in)

        return timestamp_out.replace(microsecond=0)
