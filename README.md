# TimeTrack2 - 1.0.0

[![Build Status](https://travis-ci.org/anthonyoteri/timetrack2.svg?branch=master)](https://travis-ci.org/anthonyoteri/timetrack2)
[![Coverage Status](https://coveralls.io/repos/github/anthonyoteri/timetrack2/badge.svg?branch=master)](https://coveralls.io/github/anthonyoteri/timetrack2?branch=master)

A time-tracking utility

## Installation

Install TimeTrack2 using PIP directly from github

```bash
$> pip install git+https://github.com/anthonyoteri/timetrack2.git
```

## Managing Tasks

The first thing you must do is set up one or more tasks.  Tasks are
referenced by name, so it's best to keep the name short and try to avoid
spaces and special characters which will require quoting.

For example, to create the task "project1", issue the following command.

```bash
$> tt create project1
```

If you must include spaces or special characters, quoting will be
necessary to avoid the shell from misinterpreting the name, e.g.

```bash
$> tt create "a poor choice for a task name"
```

Now you are able to view what tasks you have in the system using the
"tasks" command, e.g.

```bash
$> tt tasks
All Tasks:
  project1
```

As long as you have not worked on a project, it may be deleted.  Once
records exist for a given project, the system will prevent you from
deleting it.  A project can be deleted by issuing the "remove" command.

```bash
$> tt remove project2
```

## Working with Timers

Once you have one or more tasks in the system, you can start and stop
timers to track the time spent working.

To start a timer on "project1" use the "start" command.

```bash
$> tt start project1
```

This is equivalent to

```bash
$> tt start project1 now
```

If you forget to start a timer, and realize this later, you can specify
a time in the past.  The syntax is fairly flexible, but below are some
examples that will work.

```bash
$> tt start project1 "9 am"
...
$> tt start project1 "09:15"
...
$> tt start project1 "10 minutes ago"
...
$> tt start project1 "yesterday at 9 am EST"
```

The specified time *MUST* be in the past.  It is not possible to record
a start time in the future.

Once you have completed working on a task, you need to mark the timer as
stopped.  To do so, you use the "stop" command.  This command will stop
the last running timer at the current time, however, you may specify a
time using the same syntax as allowed for starting the time as long as
that time is both after when the timer started, and not in the future.

To stop the current timer now use:

```bash
$> tt stop
```

If you missed stopping a timer, you can use something like the following
to specify the stop time.

```bash
$> tt stop "15 minutes ago"
...
$> tt stop "5pm"
...
$> tt stop "17:15 EDT"
...
$> tt stop "2018-01-05T16:30:00+0200"
```

## Viewing Time Records

There are two ways to view time records, as aggregated per-task totals,
and as individual records.  To view the aggregated results, use the
command "summary" and to view the individual records use the command
"records"  Both take an optional `--begin` and `--end` argument which is
specified using the same formats as used when starting and stopping
timers.

To view the aggregated summary of records for the current day use:

```bash
$> tt summary --begin "midnight EDT" --end now
```

To view the individual records from this week use:

```bash
$> tt records --begin "monday at midnight EDT" --end now
```

Or for the month of January:
```bash
$> tt records --begin "january 1 at midnight EDT" \
   --end "february 1 at midnight EDT"
```

## Reporting

To view a report of the current month's activity you can use the "report" command, e.g.

```bash
$> tt report
```

To view the report for a different month, the month number can be
specified with `--month`.  Supplying a month greater than the current
month, will generate a report on that month for the previous year.

For example, if it is currently February, and you wish to view the
report for January of this year, specify `--month 1`, but if you specify
`--month 3` it will generate a report for March of the previous year.
It is not possible to generate a report for a future month, or for a
month more than 1 year ago.
