# Copyright (C) 2018, Anthony Oteri
# All rights reserved

import argparse
import calendar
from datetime import datetime, timezone
import logging
import sys

import dateparser
from tabulate import tabulate

from tt.exc import ParseError
import tt.io
from tt.sql import connect
from tt.service import TaskService, TimerService
from tt.datetime import local_time

log = logging.getLogger('tt.cli')

DEFAULT_REPORT_START = "monday at midnight UTC"
DEFAULT_REPORT_END = "now"
DATEPARSER_SETTINGS = {'TO_TIMEZONE': 'UTC', 'RETURN_AS_TIMEZONE_AWARE': True}
DEFAULT_TABLE_FORMAT = 'simple'
DEFAULT_TABLE_HEADER_FORMATTER = str.capitalize


def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser()

    parser.add_argument('-v', '--verbose', action='store_true')

    subparsers = parser.add_subparsers()

    # Commands for working with tasks

    create_parser = subparsers.add_parser('create')
    create_parser.add_argument('name', help='Task name')
    create_parser.set_defaults(func=do_create)

    tasks_parser = subparsers.add_parser('tasks')
    tasks_parser.set_defaults(func=do_tasks)

    remove_parser = subparsers.add_parser('remove')
    remove_parser.add_argument('name', help='Task name')
    remove_parser.set_defaults(func=do_remove)

    # Commands for working with timers

    start_parser = subparsers.add_parser('start')
    start_parser.add_argument('task', help='Task name')
    start_parser.add_argument(
        'time', help='timestamp', default='now', nargs='?')
    start_parser.set_defaults(func=do_start)

    stop_parser = subparsers.add_parser('stop')
    stop_parser.add_argument(
        'time', help='timestamp', default='now', nargs='?')
    stop_parser.set_defaults(func=do_stop)

    summary_parser = subparsers.add_parser('summary')
    summary_parser.add_argument(
        '--begin',
        default=DEFAULT_REPORT_START,
        help='Timestamp for start of reporting period (inclusive)')
    summary_parser.add_argument(
        '--end',
        default=DEFAULT_REPORT_END,
        help='Timestamp for end of reporting period (exclusive)')
    summary_parser.set_defaults(func=do_summary)

    records_parser = subparsers.add_parser('records')
    records_parser.add_argument(
        '--begin',
        default=DEFAULT_REPORT_START,
        help='Timestamp for start of reporting period (inclusive)')
    records_parser.add_argument(
        '--end',
        default=DEFAULT_REPORT_END,
        help='Timestamp for end of reporting period (exclusive)')
    records_parser.set_defaults(func=do_records)

    report_parser = subparsers.add_parser('report')
    report_parser.add_argument(
        '--month',
        type=int,
        choices=range(1, 13),
        help="Month to generate report for")
    report_parser.set_defaults(func=do_report)

    # Commands for import and export
    export_parser = subparsers.add_parser('export')
    export_parser.add_argument(
        'destination', help='Destination filename or - for stdout')
    export_parser.set_defaults(func=do_export)

    import_parser = subparsers.add_parser('import')
    import_parser.add_argument('source', help='Source filename or - for stdin')
    import_parser.set_defaults(func=do_import)

    args = parser.parse_args(argv)
    configure_logging(args.verbose)

    connect(echo=args.verbose)
    args.func(args)


def configure_logging(verbose=False):
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(
            level=logging.WARNING, format='%(levelname)s:%(message)s')


def do_create(args):
    log.info('create task with name %s', args.name)
    service = TaskService()
    service.add(name=args.name)


def do_tasks(args):
    log.info('list tasks')
    service = TaskService()

    table = [[t] for t in service.list()]
    headers = _format_headers(['task'])
    print(_make_table(table, headers=headers))


def do_remove(args):
    log.info('remove task with name %s', args.name)
    service = TaskService()
    service.remove(name=args.name)


def do_start(args):
    time = _parse_timestamp(args.time)
    log.info('starting timer on task %s %s', args.task, time)
    service = TimerService()
    service.start(task=args.task, timestamp=time)


def do_stop(args):
    time = _parse_timestamp(args.time)
    log.info('stopping current timer %s', time)
    service = TimerService()
    service.stop(timestamp=time)


def do_summary(args):
    begin = _parse_timestamp(args.begin)
    end = _parse_timestamp(args.end)
    log.info('presenting summary from %s to %s', begin, end)

    service = TimerService()
    headers = _format_headers(['task', 'elapsed'])
    table = service.summary(range_begin=begin, range_end=end)
    print(_make_table(table, headers=headers))


def do_records(args):
    begin = _parse_timestamp(args.begin)
    end = _parse_timestamp(args.end)
    log.info('presenting records from %s to %s', begin, end)

    service = TimerService()

    headers = _format_headers(['id', 'task', 'start', 'stop', 'elapsed'])
    table = service.records(range_begin=begin, range_end=end)
    print(_make_table(table, headers=headers))


def do_report(args):
    service = TimerService()

    target_date = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0)

    if args.month:
        if args.month > target_date.month:
            target_date = target_date.replace(year=target_date.year - 1)
        target_date = target_date.replace(month=args.month)

    last_day_of_month = calendar.monthrange(target_date.year,
                                            target_date.month)[1]

    for headers, table in service.report(
            range_begin=target_date.replace(day=1),
            range_end=target_date.replace(day=last_day_of_month)):

        print(_make_table(table, headers=headers) + '\n')


def _make_table(rows, headers):
    def convert(raw):
        if isinstance(raw, datetime):
            return local_time(raw).replace(tzinfo=None)
        return raw

    table = [[convert(c) for c in r] for r in rows]

    return tabulate(
        table, headers=_format_headers(headers), tablefmt=DEFAULT_TABLE_FORMAT)


def _format_headers(headers, formatter=DEFAULT_TABLE_HEADER_FORMATTER):
    for h in headers:
        yield formatter(h)


def _parse_timestamp(timestamp_in):
    timestamp_out = dateparser.parse(
        timestamp_in,
        settings=DATEPARSER_SETTINGS,
    )

    if timestamp_out is None:
        raise ParseError("Unable to parse %s" % timestamp_in)

    return timestamp_out.replace(microsecond=0)


def do_export(args):
    service = TimerService()
    if args.destination == '-':
        tt.io.dump(service, sys.stdout)
        return

    with open(args.destination, 'w') as out:
        tt.io.dump(service, out)


def do_import(args):
    task_service = TaskService()
    timer_service = TimerService()

    if args.source == '-':
        tt.io.load(task_service, timer_service, sys.stdin)
        return
    with open(args.source, 'r') as in_:
        tt.io.load(task_service, timer_service, in_)


def __init__():
    if __name__ == '__main__':
        sys.exit(main())


__init__()
