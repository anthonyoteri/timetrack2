# Timetrack2

A simple time tracking
utility

[![image](https://travis-ci.org/anthonyoteri/timetrack2.svg?branch=master)](https://travis-ci.org/anthonyoteri/timetrack2)

[![image](https://coveralls.io/repos/github/anthonyoteri/timetrack2/badge.svg?branch=master)](https://coveralls.io/github/anthonyoteri/timetrack2?branch=master)

# Product Changelog

## Roadmap

> TBD

## 1.0 Release

### 1.0.5

>   - Fix: Tracebacks when starting non-existing task
>   - New: Resume previous task
>   - Enhancement: Major refactoring of CLI table logic

### 1.0.4

>   - New: Additional shortcut parameters for summary and reporting
>     views
>   - New: Support for editing timer records
>   - New: Support for deleting timer records

### 1.0.3

>   - Fix: Timezone issue while grouping records in reporting views
>   - Fix: CLI should always refer to times in local timezone
>   - Enancement: Major build system refactoring

### 1.0.2

>   - Fix: Week ranges sometimes produced wrong week for edge cases.
>   - New: Show total in summary view
>   - New: Status command

### 1.0.1

>   - Fix: Column formatting across weeks in report view
>   - Fix: Default timespan for "records" view should be current day
>   - Fix: Default timespan for "summary" view should be current day
>   - New: Fancy grid now default style for tables
>   - New: Add --version command line switch

### 1.0.0

>   - First public release

# User Guide

## Tasks

### Creating Tasks

The first thing you must do is add one or more tasks. Tasks are unique
names given to an activity or project. A task is referenced by it's
name, so it's best to keep that name as short but memorable. Tasks also
may have a longer description associated with them that will be shown
along with the task in the task list. The description is optional, and
is only used for your reference when listing tasks.

To create a task, use the command \`create\`:

    $> tt create project1 "longer description of project 1"

The create command takes the parameters name and description

>   - name -- A required short identifier for the task
>   - description -- An optional description for reference

### Listing Tasks

To view the current task list use the command \`tasks\`:

    $> tt tasks

The tasks command will output a table showing the task names and
descriptions.

### Renaming Task

To change the name of a task, use the command \`rename\`:

    $> tt rename old new

The rename command takes the parameters old\_name and new\_name

>   - old\_name -- The name of an existing task
>   - new\_name -- The new task name

The new\_name value must be a unique name for the new task. All records
in associated with the old task name will be updated automatically to
use the new name.

### Updating a Task's Description

If you want to change the long description for an existing task, you can
use the describe command to do so:

    $> tt describe my_task "A new description of my task"

The describe command takes the parameters name and description.

>   - name -- The name of an existing task
>   - description -- The new description of the task. Specifying the
>     empty string "" will erase an existing description.

### Deleting a Task

It is possible to remove a task *only* if the task has not been
associated with any timer events. Once the task has been used, it is
**permanent**.

To remove an unused task, use the remove command:

    $> tt remove my_task

The remove command takes the parameter \`name\`:

>   - name -- The name of an existing, unused, task

## Timers

### Starting a Timer

When you wish to start a timer for a task, use the start command:

    $> tt start my_task

The start command takes two optional parameters task and timestamp.

>   - task -- The name of an existing task.
>   - timestamp -- Optional time when the task was started. This value
>     must be in the past, and uses a flexible format described below.

If the task parameter is missing, it will use the same task as the last
started task, effectively resuming the previous task. If there are no
existing tasks, this parameter is required.

The timestamp parameter is fairly flexible in it's notation. Below are
some examples which could be used. Keep in mind, that the start command
requires that any provided timestamps be in the past. It is **not**
possible to start a timer in the future.

>   - "2018-02-14T09:00:00-0400"
>   - "February 14 at 9am EDT"
>   - "Today at 9am EDT"
>   - "Yesterday at 9am EDT"
>   - "9am"
>   - "09:00"
>   - "Monday at 3am UTC"

### Stopping a Timer

Since only one timer can be active at a given time, it's not necessary
to tell the stop command what timer to stop, however, it will take an
optional parameter containing the timestamp in the same format as was
used by start if you wish to stop a timer at an earlier time, such as if
you forgot to stop the timer and realized it later.

To stop the active timer, use the stop command:

    $> tt stop

Stop takes only the optional timestamp field.

>   - timestamp -- Optional time when the task was stopped. This value
>     **must** be in the past, and uses the flexible format describe in
>     the start command.

### Editing a Timer

Before editing a timer, you will need to find the ID of the timer by
using the records command. See "Viewing Records" below for information
on the usage of that command.

Once you have the ID of an existing timer, you may edit the timer in the
the following ways.

>   - Deleting the timer
>   - Updating the task associated with the timer
>   - Updating the start and stop times of a timer.
>   - Makeing a stopped timer active again.

To edit a timer use the edit command:

    $> tt edit <id> [options]

Where \<id\> is the ID of the timer and \[options\] are one or more of
the following.

>   - \--delete -- Delete the timer
>   - \--start -- Set a new start time
>   - \--stop -- Set a new stop time
>   - \--task -- Set a new task.
>   - \--make-active -- Clear the stop time and make the timer the
>     active timer.

**Use care when editing a timer, many of the safe-guards in place under
normal conditions, are left unchecked in edit.** This is to allow the
user full control over modifying records in the DB. Some checks do still
occur, such as verifying that the start time comes before the stop time,
and both are in the past.

To delete timer 249::

    $> tt edit 249 --delete

To change the start and stop time of timer 53:

    $> tt edit 53 --start 'an hour ago' --stop 'now'

To make timer 199 the active timer:

    $> tt edit 199 --make-active

**WARNING: Do not change the times of a timer such that they overlap
with another timer, or the time will be double-counted, as no checks
currently are implemented to prevent this.**

**WARNING: Do not make more than one timer active at a time.**

## Viewing Records

Timetrack2 supports several different ways to view timers, either as
individual records with the records command, or as a summary where each
task is listed with the total time over a given time span with the
summary command.

Views default to includeing only those records started on the current
day. There are several baked-in options for limiting the time range to
the most common ranges. These include the current and past day, week,
month, and year. It is also possible to specify the range manually with
the --begin and --end flags.

  - Views can take the following set of options:
    
      - \--begin \[time\] -- Custom timestamp (inclusive), Default
        "Midnight"
      - \--end \[time\] -- Custom timestamp (exclusive), Default "Now"
      - \--yesterday -- Include only timers started yesterday
      - \--week -- Include only timers started this week
      - \--last-week -- Include only timers started last week
      - \--month -- Include only timers started this month
      - \--last-month -- Include only timers start last month
      - \--year -- Include only timers started this year
      - \--last-year -- Include only timers started last year

### Examples

To view a summary of the current day's records:

    $> tt summary

To view the current days records:

    $> tt records

To view the summary for yesterday:

    $> tt summary --yesterday

To view the summary for last week:

    $> tt summary --last-week

To view records from midnight to 11am:

    $> tt records --end '11 am'

To view records from 11 am:

    $> tt records --begin '11 am'

to view a summary for the first quarter of 2018:

    $> tt records --begin 'jan 1 2018 at midnight' \
       --end 'april 1 2018 at midnight'

## Monthly Reporting

The monthly report will break down a month into weeks, showing one grid
per week, where the rows represent the tasks worked on during that week,
and the columns are one-per-weekday within the week. The final column
shows the accumulated total per task for the week, and the final row in
each table shows the accumulated total of all timers per day. The bottom
right value, represents the total hours worked across all tasks in a
given week.

To show the monthly report, use the report command:

    $> tt report --month 2

The report command takes an optional --month argument with the month
number. For example to show the report for February use --month 2 If the
given month number is greater than the current month, it will report on
that month in the previous year. For example if it is currently February
of 2018, specifying --month 2 will report Febuary 2018, while --month 3
will report on March of 2017. It is not possible to report on a month
more than 1 year ago, nor is it possible to report on a month in the
future.

An example of the reporting output is:

<table style="width:89%;">
<colgroup>
<col style="width: 13%" />
<col style="width: 12%" />
<col style="width: 12%" />
<col style="width: 12%" />
<col style="width: 12%" />
<col style="width: 12%" />
<col style="width: 12%" />
</colgroup>
<tbody>
<tr class="odd">
<td>Tasks</td>
<td>Feb 05</td>
<td>Feb 06</td>
<td>Feb 07</td>
<td>Feb 08</td>
<td>Feb 09</td>
<td>Total</td>
</tr>
<tr class="even">
<td>foo</td>
<td><blockquote>
<p>06:00</p>
</blockquote></td>
<td><blockquote>
<p>00:15</p>
</blockquote></td>
<td></td>
<td></td>
<td></td>
<td>06:15</td>
</tr>
<tr class="odd">
<td>bar</td>
<td></td>
<td><blockquote>
<p>03:00</p>
</blockquote></td>
<td></td>
<td></td>
<td></td>
<td>03:00</td>
</tr>
<tr class="even">
<td>TOTAL</td>
<td><blockquote>
<p>06:00</p>
</blockquote></td>
<td><blockquote>
<p>03:15</p>
</blockquote></td>
<td></td>
<td></td>
<td></td>
<td>09:15</td>
</tr>
</tbody>
</table>

## Status Report

On any given day, it is possible to view the status reporting for that
day by issuing the status command. The status command does not take any
arguments.

To show today's status report use the status command:

    $> tt status

An example of the reporting output is:

<table style="width:89%;">
<colgroup>
<col style="width: 13%" />
<col style="width: 12%" />
<col style="width: 12%" />
<col style="width: 12%" />
<col style="width: 12%" />
<col style="width: 12%" />
<col style="width: 12%" />
</colgroup>
<tbody>
<tr class="odd">
<td>Tasks</td>
<td>Feb 05</td>
<td>Feb 06</td>
<td>Feb 07</td>
<td>Feb 08</td>
<td>Feb 09</td>
<td>Total</td>
</tr>
<tr class="even">
<td>foo</td>
<td><blockquote>
<p>06:00</p>
</blockquote></td>
<td><blockquote>
<p>08:05</p>
</blockquote></td>
<td></td>
<td></td>
<td></td>
<td>08:05</td>
</tr>
<tr class="odd">
<td>bar</td>
<td></td>
<td><blockquote>
<p>00:20</p>
</blockquote></td>
<td></td>
<td></td>
<td></td>
<td>00:20</td>
</tr>
<tr class="even">
<td>TOTAL</td>
<td><blockquote>
<p>06:00</p>
</blockquote></td>
<td><blockquote>
<p>03:15</p>
</blockquote></td>
<td></td>
<td></td>
<td></td>
<td>09:15</td>
</tr>
</tbody>
</table>

<table style="width:100%;">
<colgroup>
<col style="width: 8%" />
<col style="width: 13%" />
<col style="width: 31%" />
<col style="width: 30%" />
<col style="width: 16%" />
</colgroup>
<tbody>
<tr class="odd">
<td>ID</td>
<td><blockquote>
<p>Task</p>
</blockquote></td>
<td><blockquote>
<p>Start</p>
</blockquote></td>
<td><blockquote>
<p>Stop</p>
</blockquote></td>
<td><blockquote>
<p>Elapsed</p>
</blockquote></td>
</tr>
<tr class="even">
<td>12</td>
<td><blockquote>
<p>foo</p>
</blockquote></td>
<td><blockquote>
<p>2018-02-06 09:00:00</p>
</blockquote></td>
<td>2018-02-06 11:35:00</td>
<td><blockquote>
<p>02:35</p>
</blockquote></td>
</tr>
<tr class="odd">
<td>13</td>
<td><blockquote>
<p>bar</p>
</blockquote></td>
<td><blockquote>
<p>2018-02-06 11:40:00</p>
</blockquote></td>
<td>2018-02-06 12:00:00</td>
<td><blockquote>
<p>00:20</p>
</blockquote></td>
</tr>
<tr class="even">
<td>14</td>
<td><blockquote>
<p>foo</p>
</blockquote></td>
<td><blockquote>
<p>2018-02-06 12:00:00</p>
</blockquote></td>
<td>2018-02-06 17:35:00</td>
<td><blockquote>
<p>05:35</p>
</blockquote></td>
</tr>
</tbody>
</table>

# LICENSE

Copyright 2018 Anthony Oteri

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

1.  Redistributions of source code must retain the above copyright
    notice, this list of conditions and the following disclaimer.
2.  Redistributions in binary form must reproduce the above copyright
    notice, this list of conditions and the following disclaimer in the
    documentation and/or other materials provided with the distribution.
3.  Neither the name of the copyright holder nor the names of its
    contributors may be used to endorse or promote products derived from
    this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
