# Copyright (C) 2018, Anthony Oteri
# All rights reserved

import argparse
import calendar
import contextlib
from datetime import datetime, timedelta
import logging
import os
import sys

import dateparser
import tabulate

import tt
from tt.datatable import Datatable
from tt.datetime import (local_time, start_of_day, start_of_week,
                         start_of_month, start_of_year, tz_local)
from tt.exc import BadRequest, ParseError
import tt.io
from tt.sql import connect
from tt.service import TaskService, TimerService, ReportingService

log = logging.getLogger('tt.cli')

DEFAULT_REPORT_START = "midnight"
DEFAULT_REPORT_END = "tomorrow at midnight"
DATEPARSER_SETTINGS = {'TO_TIMEZONE': 'UTC', 'RETURN_AS_TIMEZONE_AWARE': True}
DEFAULT_TABLE_FORMAT = 'fancy_grid'
DEFAULT_TABLE_HEADER_FORMATTER = str.capitalize
APP_DATA_DIR = "~/.timetrack2"

tabulate.PRESERVE_WHITESPACE = True


def main(argv=None):
    parser = argparse.ArgumentParser(description=tt.__DESCRIPTION__)

    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-V', '--version', action='store_true')

    subparsers = parser.add_subparsers()

    # Commands for working with tasks

    create_parser = subparsers.add_parser('create')
    create_parser.add_argument('name', help='Task name')
    create_parser.add_argument(
        'description', help='Long description', nargs='?')
    create_parser.set_defaults(func=do_create)

    describe_parser = subparsers.add_parser('describe')
    describe_parser.add_argument('name', help='Task name')
    describe_parser.add_argument(
        'description', help='Task description', nargs='?')
    describe_parser.set_defaults(func=do_describe)

    rename_parser = subparsers.add_parser('rename')
    rename_parser.add_argument('old_name', help='Existing task name')
    rename_parser.add_argument('new_name', help='New task name')
    rename_parser.set_defaults(func=do_rename)

    tasks_parser = subparsers.add_parser('tasks')
    tasks_parser.set_defaults(func=do_tasks)

    remove_parser = subparsers.add_parser('remove')
    remove_parser.add_argument('name', help='Task name')
    remove_parser.set_defaults(func=do_remove)

    # Commands for working with timers

    start_parser = subparsers.add_parser('start')
    start_parser.add_argument('task', help='Task name', nargs='?')
    start_parser.add_argument(
        'time', help='timestamp', default='now', nargs='?')
    start_parser.set_defaults(func=do_start)

    stop_parser = subparsers.add_parser('stop')
    stop_parser.add_argument(
        'time', help='timestamp', default='now', nargs='?')
    stop_parser.set_defaults(func=do_stop)

    edit_parser = subparsers.add_parser('edit')
    edit_parser.add_argument('id', type=int, help='ID of the timer to edit')
    edit_parser.add_argument(
        '--delete', action='store_true', help='delete the timer')
    edit_parser.add_argument('--task', help='Set task')
    edit_parser.add_argument('--start-time', help='Set start time')
    edit_parser.add_argument('--stop-time', help='Set stop time')
    edit_parser.add_argument(
        '--make-active',
        action='store_true',
        help='Mark timer as active/running')
    edit_parser.set_defaults(func=do_edit)

    # Commands for working with reporting

    summary_parser = subparsers.add_parser('summary')
    summary_parser.add_argument(
        '--begin', help='Timestamp for start of reporting period (inclusive)')
    summary_parser.add_argument(
        '--end', help='Timestamp for end of reporting period (exclusive)')
    summary_time_shortcuts = summary_parser.add_mutually_exclusive_group()
    summary_time_shortcuts.add_argument('--yesterday', action='store_true')
    summary_time_shortcuts.add_argument('--week', action='store_true')
    summary_time_shortcuts.add_argument('--last-week', action='store_true')
    summary_time_shortcuts.add_argument('--month', action='store_true')
    summary_time_shortcuts.add_argument('--last-month', action='store_true')
    summary_time_shortcuts.add_argument('--year', action='store_true')
    summary_time_shortcuts.add_argument('--last-year', action='store_true')
    summary_parser.set_defaults(func=do_summary)

    records_parser = subparsers.add_parser('records')
    records_parser.add_argument(
        '--begin', help='Timestamp for start of reporting period (inclusive)')
    records_parser.add_argument(
        '--end', help='Timestamp for end of reporting period (exclusive)')
    records_time_shortcuts = records_parser.add_mutually_exclusive_group()
    records_time_shortcuts.add_argument('--yesterday', action='store_true')
    records_time_shortcuts.add_argument('--week', action='store_true')
    records_time_shortcuts.add_argument('--last-week', action='store_true')
    records_time_shortcuts.add_argument('--month', action='store_true')
    records_time_shortcuts.add_argument('--last-month', action='store_true')
    records_time_shortcuts.add_argument('--year', action='store_true')
    records_time_shortcuts.add_argument('--last-year', action='store_true')
    records_parser.set_defaults(func=do_records)

    report_parser = subparsers.add_parser('report')
    report_parser.add_argument(
        '--month',
        type=int,
        choices=range(1, 13),
        help="Month to generate report for")
    report_parser.set_defaults(func=do_report)

    status_parser = subparsers.add_parser('status')
    status_parser.set_defaults(func=do_status)

    # Commands for import and export

    export_parser = subparsers.add_parser('export')
    export_parser.add_argument(
        'destination', help='Destination filename or - for stdout')
    export_parser.set_defaults(func=do_export)

    import_parser = subparsers.add_parser('import')
    import_parser.add_argument('source', help='Source filename or - for stdin')
    import_parser.set_defaults(func=do_import)

    args = parser.parse_args(argv or sys.argv[1:])
    if args.version:
        print("Timetrack2-%s" % tt.__VERSION__)
        return 0

    configure_logging(args.verbose)

    db_file = os.path.expanduser(os.path.join(APP_DATA_DIR, "timetrack2.db"))
    with contextlib.suppress(OSError):
        os.makedirs(os.path.dirname(db_file))

    connect(db_url="sqlite:///%s" % db_file, echo=args.verbose)
    try:
        args.func(args)
    except BadRequest as err:
        print("Error: %s" % err)
        return 1


def configure_logging(verbose=False):
    """
    Initialize and configure the logging.

    :param verbose: Use debug level logging. (Default value = False)

    """
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(
            level=logging.WARNING, format='%(levelname)s:%(message)s')


def do_create(args):
    log.info('create task with name %s', args.name)
    service = TaskService()
    service.add(name=args.name, description=args.description)
    print('Added task "%s" with description "%s"' % (args.name,
                                                     args.description))


def do_describe(args):
    log.info('add description to task with name %s', args.name)
    service = TaskService()
    service.describe(name=args.name, description=args.description)
    print('Described task %s as "%s"' % (args.name, args.description))


def do_rename(args):
    log.info('rename task %s to %s', args.old_name, args.new_name)
    service = TaskService()
    service.rename(old_name=args.old_name, new_name=args.new_name)
    print('Renamed task "%s" to "%s"' % (args.old_name, args.new_name))


def do_tasks(args):
    log.info('list tasks')
    service = TaskService()

    table = Datatable(label_header='Task', table_fmt='fancy_grid')
    for task, description in service.list():
        table.append({'description': description}, label=task)
    print(table)


def do_remove(args):
    log.info('remove task with name %s', args.name)
    service = TaskService()
    service.remove(name=args.name)
    print('Removed task "%s"' % args.name)


def do_start(args):
    time = _parse_timestamp(args.time)
    log.info('starting timer on task %s %s', args.task, time)
    service = TimerService()
    service.start(task=args.task, timestamp=time)
    print('Started at "%s"' % time)


def do_stop(args):
    time = _parse_timestamp(args.time)
    log.info('stopping current timer %s', time)
    service = TimerService()
    service.stop(timestamp=time)
    print('Stopped at "%s"' % time)


def do_edit(args):
    log.info("edit timer %s", args.id)

    service = TimerService()

    if args.delete:
        service.delete(id=args.id)
        print("Deleted timer %s" % args.id)

    if args.start_time or args.stop_time or args.task:
        start, stop = None, None
        if args.start_time:
            start = _parse_timestamp(args.start_time)
            print('Updating start time for timer "%s" to "%s"' % (args.id,
                                                                  start))
        if args.stop_time:
            stop = _parse_timestamp(args.stop_time)
            print('Updating stop time for timer "%s" to "%s"' % (args.id,
                                                                 stop))

        if args.task:
            print('Updating task for timer "%s" to "%s"' % (args.id,
                                                            args.task))

        service.update(id=args.id, task=args.task, start=start, stop=stop)

    if args.make_active:
        service.update(id=args.id, stop='')
        print('Marking timer "%s" as active' % args.id)


def do_summary(args):

    if args.begin or args.end:
        begin = _parse_timestamp(args.begin or DEFAULT_REPORT_START)
        end = _parse_timestamp(args.end or DEFAULT_REPORT_END)
    else:
        begin, end = from_timerange(args)

    timer_service = TimerService()
    reporting_service = ReportingService(timer_service)

    print(reporting_service.summary_by_task(start=begin, end=end))


def do_records(args):

    if args.begin or args.end:
        begin = _parse_timestamp(args.begin or DEFAULT_REPORT_START)
        end = _parse_timestamp(args.end or DEFAULT_REPORT_END)
    else:
        begin, end = from_timerange(args)

    timer_service = TimerService()
    reporting_service = ReportingService(timer_service)

    for daily_table in reporting_service.timers_by_day(start=begin, end=end):
        print("%s\n" % daily_table)


def do_report(args):
    timer_service = TimerService()
    reporting_service = ReportingService(timer_service)

    target_date = datetime.now(tz_local()).replace(
        hour=0, minute=0, second=0, microsecond=0)

    if args.month:
        if args.month > target_date.month:
            target_date = target_date.replace(year=target_date.year - 1)
        target_date = target_date.replace(month=args.month)

    last_day_of_month = calendar.monthrange(target_date.year,
                                            target_date.month)[1]

    start = target_date.replace(day=1)
    end = target_date.replace(day=last_day_of_month)
    for weekly_report in reporting_service.summary_by_day_and_task(
            start=start, end=end):
        print("%s\n" % weekly_report)


def do_status(args):
    timer_service = TimerService()
    reporting_service = ReportingService(timer_service)

    now = datetime.now(tz_local()).replace(
        hour=0, minute=0, second=0, microsecond=0)

    week_begin, week_end = tt.datetime.week_boundaries(now)

    day_begin = now
    day_end = now + timedelta(days=1)
    try:
        print(
            next(
                reporting_service.summary_by_day_and_task(
                    start=week_begin, end=week_end)))
        print('\n')
        print(
            next(
                reporting_service.timers_by_day(start=day_begin, end=day_end)))
    except StopIteration:
        print("No records")


def _parse_timestamp(timestamp_in):
    """
    Parse flexible timestamp strings, like "tomorrow at 8am".

    :param timestamp_in: A string description of the time.
    :returns: A timezone aware python datetime object.
    :raises: ParseError if the timestamp string is not parsable.
    """
    timestamp_out = dateparser.parse(
        timestamp_in,
        settings=DATEPARSER_SETTINGS,
    )

    if timestamp_out is None:
        raise ParseError("Unable to parse %s" % timestamp_in)

    return local_time(timestamp_out.replace(microsecond=0))


def from_timerange(args):
    """Return datetimes for timetranges specified in the arguments.

    Allowed timeranges are:
      * yesterday
      * week
      * last_week
      * month
      * last_month
      * year
      * last_year

    :param args: parsed command line arguments.
    :returns: A tuple of timezone aware datetime objects representing
              the start (inclusive) and end (exclusive) for the given
              timerange, or the start and end of the current day if not
              specified.
    """
    now = datetime.now(tz_local())

    if args.yesterday:
        return start_of_day(now - timedelta(days=1)), start_of_day(now)

    if args.week:
        return start_of_week(now), start_of_week(now + timedelta(days=7))

    if args.last_week:
        return start_of_week(now - timedelta(days=7)), start_of_week(now)

    if args.month:
        return (start_of_month(now.replace(day=15)),
                start_of_month(now.replace(day=15) + timedelta(days=30)))

    if args.last_month:
        return (start_of_month(now.replace(day=15) - timedelta(days=30)),
                start_of_month(now.replace(day=15)))

    if args.year:
        return start_of_year(now), start_of_year(now + timedelta(days=365))

    if args.last_year:
        return start_of_year(now - timedelta(days=365)), start_of_year(now)

    return start_of_day(now), start_of_day(now + timedelta(days=1))


def do_export(args):
    service = TimerService()
    if args.destination == '-':
        tt.io.dump(service, sys.stdout)
        return

    with open(args.destination, 'w') as out:
        print("Exporting records to %s" % args.destination)
        tt.io.dump(service, out)


def do_import(args):
    task_service = TaskService()
    timer_service = TimerService()

    if args.source == '-':
        tt.io.load(task_service, timer_service, sys.stdin)
        return
    with open(args.source, 'r') as in_:
        print('Importing records from %s' % args.source)
        tt.io.load(task_service, timer_service, in_)


def __init__():
    if __name__ == '__main__':
        sys.exit(main())


__init__()
