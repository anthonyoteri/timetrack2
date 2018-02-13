# Copyright (C) 2018, Anthony Oteri
# All rights reserved.

from datetime import datetime, timedelta, timezone
import json

import iso8601

from tt.exc import ValidationError


def dump(service, out):
    begin = datetime(1970, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    end = datetime.now(timezone.utc)

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
        timer_service.start(task=obj['task'], timestamp=timestamp)
        timer_service.stop(
            timestamp=timestamp + timedelta(seconds=int(obj['elapsed'])))
