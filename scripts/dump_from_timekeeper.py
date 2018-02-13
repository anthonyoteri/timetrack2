# Copyright (C) 2018, Anthony Oteri
# All rights reserved.

# Helper script to dump timekeeper's database to a suitable format for
# importing into timetrack2

from datetime import datetime, timedelta, timezone
import json
import sys

import sqlite3

conn = sqlite3.connect(sys.argv[1])

c = conn.cursor()

for project, start, elapsed in c.execute(
        'SELECT project, start, elapsed FROM record'):
    timestamp = datetime(
        1970, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=start)

    if elapsed == 0:
        elapsed = (datetime.now(timezone.utc) - timestamp).total_seconds()

    record = {
        'task': project,
        'start': timestamp.isoformat() + 'Z',
        'elapsed': int(elapsed),
    }

    print(json.dumps(record))

c.close()
