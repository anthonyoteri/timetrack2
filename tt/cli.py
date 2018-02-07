# Copyright (C) 2018, Anthony Oteri
# All rights reserved

import argparse
import logging
import sys

import dateparser

from tt.exc import ParseError
from tt.sql import connect
from tt.service import TaskService, TimerService

log = logging.getLogger('tt.cli')

DEFAULT_REPORT_START = "monday at midnight UTC"
DEFAULT_REPORT_END = "now"
DATEPARSER_SETTINGS = {'TO_TIMEZONE': 'UTC', 'RETURN_AS_TIMEZONE_AWARE': False}


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

    args = parser.parse_args(argv)
    configure_logging(args.verbose)

    connect(echo=args.verbose)
    try:
        args.func(args)
    except AttributeError:
        parser.print_usage()
        raise SystemExit(1)


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

    print('All Tasks')
    for task in service.list():
        print("  %s" % task)


def do_remove(args):
    log.info('remove task with name %s', args.name)
    service = TaskService()
    service.remove(name=args.name)


def do_start(args):
    log.info('starting timer on task %s %s', args.task, args.time)
    service = TimerService()
    service.start(task=args.task, timestamp=args.time)


def do_stop(args):
    log.info('stopping current timer %s', args.time)
    service = TimerService()
    service.stop(timestamp=args.time)


def do_summary(args):
    begin = _parse_timestamp(args.begin)
    end = _parse_timestamp(args.end)
    log.info('presenting summary from %s to %s', begin, end)

    service = TimerService()
    print("Summary from %s to %s" % (args.begin, args.end))

    for task, elapsed in service.summary(range_begin=begin, range_end=end):
        print("  %s %s" % (task, elapsed))


def do_records(args):
    begin = _parse_timestamp(args.begin)
    end = _parse_timestamp(args.end)
    log.info('presenting records from %s to %s', begin, end)

    service = TimerService()
    print("Records from %s to %s" % (args.begin, args.end))

    for id, task, start, stop, elapsed in service.records(
            range_begin=begin, range_end=end):
        print(" %s %s %s %s %s" % (id, task, start, stop, elapsed))


def _parse_timestamp(timestamp_in):
    timestamp_out = dateparser.parse(
        timestamp_in,
        settings=DATEPARSER_SETTINGS,
    )

    if timestamp_out is None:
        raise ParseError("Unable to parse %s" % timestamp_in)

    return timestamp_out.replace(microsecond=0)


if __name__ == '__main__':
    main()
