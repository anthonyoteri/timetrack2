# Copyright (C) 2018, Anthony Oteri
# All rights reserved.

from datetime import timedelta
import json

import iso8601

from tt.exc import ValidationError


def dump(service, out):
    """
    Create a dump file of each record in JSON format.

    The generated file contains one record per line, e.g.

    {"task": "foo", "start": "2018-02-14T00:00:00+00:00", "elapsed": 300}
    {"task": "bar", "start": "2018-02-14T00:05:00+00:00", "elapsed": 600}

    :param service: The TimerService instance
    :param out: A file-like object where to dump the records.
    """
    for _, timers in service.slice_grouped_by_date():
        for timer in timers:
            record = {
                'task': timer['task'],
                'start': timer['start'].isoformat(),
                'elapsed': int(timer['elapsed'].total_seconds())
            }
        json.dump(record, out)
        out.write('\n')


def load(task_service, timer_service, lines):
    """
    Load records from a dump.

    Each line should contain a JSON formatted string containing the following
    fields:

    * "task" - The name of the task
    * "start" - An iso8601 formatted date string including the timezone.
    * "elapsed" - The integer number of seconds.

    :param task_service: The TaskService instance
    :param timer_service: The TimerService instance
    :param lines: An iterable of json-formatted lines, each containing one
                  record.
    """

    for line in lines:
        obj = json.loads(line.strip())
        try:
            task_service.add(name=obj['task'])
        except ValidationError:
            pass

        timestamp = iso8601.parse_date(obj['start'])
        timer_service.start(task=obj['task'], timestamp=timestamp)
        timer_service.stop(
            timestamp=timestamp + timedelta(seconds=int(obj['elapsed'])))
