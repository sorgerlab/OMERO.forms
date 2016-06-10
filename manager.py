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



# TODO Delete Form
# TODO Delete data
# TODO Delete kv?









if __name__ == '__main__':
    handler = ArgumentHandler()

    handler.add_argument('--master', '-m', type=long, required=True,
                         help='User ID of the forms master')

    handler.run()











# # Add a key-value to the group
# form1 = """
# {
#     "title": "Form One",
#     "type": "object",
#     "required": ["project", "someNumber"],
#     "properties": {
#       "project": {"type": "string", "title": "Project Name"},
#       "something": {"type": "boolean", "title": "Something?", "default": false},
#       "someNumber": {"type": "number", "title": "Some number"}
#     }
# }
# """
#
# ui1 = """
# {
#   "someNumber": {
#     "ui:widget": "updown"
#   }
#
# }
# """
#
# form2 = """
# {
#     "title": "Form Two",
#     "type": "object",
#     "required": ["project", "someNumber"],
#     "properties": {
#       "project": {"type": "string", "title": "Project Name"},
#       "something": {"type": "boolean", "title": "Something?", "default": false},
#       "someNumber": {"type": "number", "title": "Some number"}
#     }
# }
# """
#
# ui2 = """
# {
#   "someNumber": {
#     "ui:widget": "updown"
#   }
#
# }
# """
#
# form_basic = """
# {
#   "title": "Basic Experimental Metadata",
#   "type": "object",
#   "required": [
#     "description",
#     "cellType",
#     "formType",
#     "controlType",
#     "labellingProtocol"
#   ],
#   "properties": {
#     "description": {
#       "type": "string",
#       "title": "Description"
#     },
#     "cellType": {
#       "type": "string",
#       "title": "Cell type"
#     },
#     "formType": {
#       "type": "string",
#       "enum": [
#         "Experiment",
#         "Assay Development",
#         "Other"
#       ],
#       "title": "Type",
#       "uniqueItems": true
#     },
#     "controlType": {
#       "type": "string",
#       "enum": ["Positive", "Negative"],
#       "title": "Control Type"
#     },
#     "labellingProtocol": {
#       "type": "string",
#       "title": "Labelling Protocol"
#     }
#   }
# }
# """
#
# ui_basic = """
# {
#   "description": {
#     "ui:widget": "textarea"
#   },
#   "formType": {
#     "ui:widget": "radio"
#   },
#   "controlType": {
#     "ui:widget": "radio"
#   },
#   "labellingProtocol": {
#     "ui:widget": "textarea"
#   }
# }
# """
#
# form1_data = json.dumps({
#     'project': 'My first project',
#     'something': True,
#     'someNumber': 12345
# })
#
# master_user_id = 252L
# form_id = 'form1'
# form_schema = form1
# ui_schema = ui1
# group_ids = [203L]

# Add a form for datasets
# utils.add_form(su_conn, master_user_id, 'form1', form1, ui1,
#                [203L], ['Dataset'])

# Add a form for projects
# utils.add_form(su_conn, master_user_id, 'form2', form2, ui2,
#                [203L], ['Project'])

# Add a form for datasets and plates
# utils.add_form(su_conn, master_user_id, 'basic', form_basic, ui_basic,
#                [203L], ['Dataset', 'Plate'])

# List all the forms
# for form in utils.list_forms(su_conn, master_user_id):
#     pprint(form)

# List all the forms in a group
# for form in utils.list_forms(su_conn, master_user_id, 203L):
#     pprint(form)

# List all the forms in a group for datasets
# for form in utils.list_forms(su_conn, master_user_id, 203L, 'Dataset'):
#     pprint(form)

# List all the forms in a group for projects
# for form in utils.list_forms(su_conn, master_user_id, 203L, 'Project'):
#     pprint(form)

# Get a form
# pprint(utils.get_form(su_conn, master_user_id, form_id))

# Delete a form
# utils.delete_form(su_conn, master_user_id, form_id)
# utils.delete_form(su_conn, master_user_id, 'basic')

# Add data for a form
# utils.add_form_data(su_conn, master_user_id, form_id, 'Dataset', 251L,
#                     form1_data, 'rou', datetime.now())

# Get data for a form
# print 'Changed At\t\t', '\tChanged By', '\tForm Data'
# for form_data in utils.get_form_data_history(su_conn, master_user_id, 'basic',
#                                              'Dataset', 251L):
#     # print(form_data)
#     print form_data['changed_at'], '\t', form_data['changed_by'], '\t\t',  form_data['form_data']

# Get latest data for a form
# pprint(utils.get_form_data(su_conn, master_user_id, form_id, 'Dataset', 251L))

# Delete data for a form
# utils.delete_form_data(su_conn, master_user_id, form_id, 'Dataset', 251L)

# utils.add_form_data_to_obj(conn, form_id, 'Dataset', 251L, form1_data)

# utils.delete_form_kvdata(conn, form_id, 'Dataset', 251L)

# for orphan in utils.list_form_data_orphans(conn, 252L):
#     print orphan
