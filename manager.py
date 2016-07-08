#!/usr/bin/env python

from arghandler import ArgumentHandler, subcmd
from omero_basics import OMEROConnectionManager
from datetime import datetime
import json
import utils
from tabulate import tabulate
import sys
import os

TRUNCATE_LENGTH = 200

# Create ordinary and form master connection
# conn_manager = OMEROConnectionManager(config_file="omero.cfg")
# conn = conn_manager.connect()
conn_manager = OMEROConnectionManager(config_file="omero_su.cfg")
conn = conn_manager.connect()


def print_form_list(master_id, group_id=None, obj_type=None):
    """ Print the list of available forms. Optionally filtered"""

    forms = utils.list_forms(conn, master_id, group_id, obj_type)

    headers = ['Form ID', 'Group IDs', 'Object Types']

    print tabulate(
        [
            [
                form['form_id'],
                ','.join(str(group_id) for group_id in form['group_ids']),
                ','.join(form['obj_types'])
            ] for form in forms
        ],
        headers=headers
    )


def print_form(master_id, form_id):
    """ Print the details of a form """

    form = utils.get_form(conn, master_id, form_id)

    if not form:
        print 'ERROR: No such form'
        sys.exit(1)

    print tabulate(
        [
            ['Form ID:', form['form_id']],
            [
                'Group IDs:',
                ','.join(str(group_id) for group_id in form['group_ids'])
            ],
            ['Object Types:', ','.join(form['obj_types'])]
        ],
        tablefmt="plain"
    )
    print 'Schema:'
    print(form['json_schema'])
    print 'UI:'
    print(form['ui_schema'])


def truncate_string(s, t):
    if t is None or t > len(s):
        return s
    return s[:t] + '...'


def print_history(master_id, form_id, obj_type, obj_id, truncate):

    entries = utils.get_form_data_history(conn, master_id, form_id,
                                          obj_type, obj_id)

    entries = list(entries)

    if len(entries) == 0:
        print 'No entries for %s, %s, %s' % (form_id, obj_type, obj_id)
        sys.exit(0)

    headers = ['Changed At', 'Changed By', 'Form Data']

    print tabulate(
        [
            [
                entry['changed_at'],
                entry['changed_by'],
                truncate_string(entry['form_data'], truncate)
            ] for entry in entries
        ],
        headers=headers
    )


def print_orphans(master_id):
    orphans = utils.list_form_data_orphans(conn, 252L)

    headers = ['Form ID', 'Object Type', 'Object ID']

    print tabulate(
        [
            [
                orphan['form_id'],
                orphan['obj_type'],
                orphan['obj_id']
            ] for orphan in orphans
        ],
        headers=headers
    )


def add_form(master_id, form_id, json_schema, ui_schema, group_ids, obj_types):
    # TODO Try
    utils.add_form(conn, master_id, form_id, json_schema, ui_schema,
                   group_ids, obj_types)


def delete_form(master_id, form_id):
    # TODO Try
    utils.delete_form(conn, master_id, form_id)


@subcmd('list')
def form_list(parser, context, args):

    parser.add_argument('--group', '-g', type=long,
                        help='Group ID to filter by')

    parser.add_argument('--type', '-t',
                        choices=['Project', 'Dataset', 'Screen', 'Plate'],
                        help='Object type to filter by')

    args = parser.parse_args(args)

    print_form_list(context.master, args.group, args.type)


@subcmd('info')
def form_info(parser, context, args):

    parser.add_argument('form', help='Form ID to print')

    args = parser.parse_args(args)

    print_form(context.master, args.form)


@subcmd('history')
def form_history(parser, context, args):

    parser.add_argument('form',
                        help='Form ID to get history for')

    parser.add_argument('type',
                        choices=['Project', 'Dataset', 'Screen', 'Plate'],
                        help='Object type to get history for')

    parser.add_argument('object', type=long,
                        help='Object ID to get history for')

    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose')

    args = parser.parse_args(args)

    print_history(context.master, args.form, args.type, args.object,
                  truncate=None if args.verbose else TRUNCATE_LENGTH)


@subcmd('orphans')
def form_orphans(parser, context, args):

    print_orphans(context.master)


def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return open(arg, 'r')  # return an open file handle


@subcmd('add')
def form_add(parser, context, args):

    parser.add_argument('form',
                        help='Form ID to add (Must be globally unique)')

    parser.add_argument('schema',
                        type=lambda f: is_valid_file(parser, f),
                        metavar="FILE",
                        help='input file with schema')

    parser.add_argument('ui',
                        type=lambda f: is_valid_file(parser, f),
                        metavar="FILE",
                        help='input file with ui')

    parser.add_argument('--types', '-t',
                        nargs='+',
                        choices=['Project', 'Dataset', 'Screen', 'Plate'],
                        default=[],
                        help='Object types to add form for (Space separated)')

    parser.add_argument('--groups', '-g',
                        nargs='+',
                        type=long,
                        default=[],
                        help='Group IDs to add form for (Space separated)')

    args = parser.parse_args(args)

    schema = args.schema.read()
    args.schema.close()

    ui = args.ui.read()
    args.ui.close()

    add_form(context.master, args.form, schema, ui, args.groups, args.types)


@subcmd('delete')
def form_delete(parser, context, args):

    parser.add_argument('form',
                        help='Form ID to delete')

    args = parser.parse_args(args)

    delete_form(context.master, args.form)


# TODO Delete data
# TODO Delete kv?
# TODO Update form groups/object types

def formmaster(value):
    try:
        return long(value)
    except ValueError:
        pass

    # TODO Try-catch
    return utils.get_formmaster_id(conn, value)

if __name__ == '__main__':
    handler = ArgumentHandler()

    handler.add_argument('--master', '-m', type=formmaster, required=True,
                         help='User ID of the forms master')

    handler.run()
