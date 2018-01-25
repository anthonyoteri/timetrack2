# Copyright (C) 2018, Anthony Oteri
# All rights reserved

from __future__ import absolute_import, division, print_function

import argparse
from datetime import datetime
import logging

from tt.db import connect
import tt.task
import tt.timer


log = logging.getLogger('tt.cli')


def main():
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
    start_parser.set_defaults(func=do_start)

    stop_parser = subparsers.add_parser('stop')
    stop_parser.add_argument('timer', help="Timer ID or Task Name")
    stop_parser.set_defaults(func=do_stop)

    cancel_parser = subparsers.add_parser('cancel')
    cancel_parser.add_argument('timer', help='Timer ID or Task Name')
    cancel_parser.set_defaults(func=do_cancel)

    update_parser = subparsers.add_parser('update')
    update_parser.add_argument('timer', help='Timer ID or Task Name')
    update_command_group = update_parser.add_mutually_exclusive_group(
            required=True)
    update_command_group.add_argument('--task', action='store_true')
    update_command_group.add_argument('--start', action='store_true')
    update_parser.add_argument('value')
    update_parser.set_defaults(func=do_update)

    timers_parser = subparsers.add_parser('timers')
    timers_parser.set_defaults(func=do_timers)

    history_parser = subparsers.add_parser('history')
    history_parser.set_defaults(func=do_history)

    summarize_parser = subparsers.add_parser('summary')
    summarize_parser.set_defaults(func=do_summarize)

    args = parser.parse_args()
    configure_logging(args.verbose)

    connect(echo=args.verbose)
    args.func(args)


def configure_logging(verbose=False):
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.WARNING,
                            format='%(levelname)s:%(message)s')


def do_create(args):
    log.info('create task with name %s', args.name)
    tt.task.create(args.name)


def do_tasks(args):
    log.info('list tasks')
    tt.task.list()


def do_remove(args):
    log.info('remove task with name %s', args.name)
    tt.task.remove(args.name)


def do_start(args):
    log.info('start timer')
    tt.timer.start(args.task, datetime.utcnow())


def do_stop(args):
    log.info('stop timer')
    tt.timer.stop(args.timer, datetime.utcnow())


def do_cancel(args):
    log.info('cancel timer')
    tt.timer.cancel(args.timer)


def do_update(args):
    log.info('update timer')

    if args.task:
        tt.timer.update_task(args.timer, args.value)
    elif args.start:
        tt.timer.update_start(args.timer, args.value)


def do_timers(args):
    log.info('show timers')
    tt.timer.timers()


def do_history(args):
    log.info('show history')
    tt.timer.history()


def do_summarize(args):
    log.info('show summary')
    tt.timer.summarize()


if __name__ == '__main__':
    main()
