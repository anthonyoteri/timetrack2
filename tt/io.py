# Copyright (C) 2018, Anthony Oteri
# All rights reserved.

from datetime import date, datetime, timedelta
import json

import iso8601

from tt.exc import ValidationError


def dump(service, out):
    begin = date(1970, 1, 1)
    end = datetime.utcnow()

    for _, task, start, _, elapsed in service.records(
            range_begin=begin, range_end=end):
        record = {
            'task': task,
            'start': start.isoformat(),
            'elapsed': int(elapsed.total_seconds())
        }
        json.dump(record, out)
        out.write('\n')


def load(task_service, timer_service, lines):

    for line in lines:
        obj = json.loads(line.strip())
        try:
            task_service.add(name=obj['task'])
        except ValidationError:
            pass

        timestamp = iso8601.parse_date(obj['start'])
        timestamp = timestamp.replace(tzinfo=None)
        timer_service.start(task=obj['task'], timestamp=timestamp)
        timer_service.stop(
            timestamp=timestamp + timedelta(seconds=int(obj['elapsed'])))
