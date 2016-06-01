from omero_basics import OMEROConnectionManager
from pprint import pprint
from datetime import datetime
import json

import utils

conn_manager = OMEROConnectionManager()
conn = conn_manager.connect()

# Add a key-value to the group
form1 = """
{
    "title": "Form One",
    "type": "object",
    "required": ["project", "someNumber"],
    "properties": {
      "project": {"type": "string", "title": "Project Name"},
      "something": {"type": "boolean", "title": "Something?", "default": false},
      "someNumber": {"type": "number", "title": "Some number"}
    }
}
"""

ui1 = """
{
  "someNumber": {
    "ui:widget": "updown"
  }
}
"""

form2 = """
{
  "title": "Date and time widgets",
  "type": "object",
  "properties": {
    "native": {
      "title": "Native",
      "description": "May not work on some browsers, notably Firefox Desktop and IE.",
      "type": "object",
      "properties": {
        "datetime": {
          "type": "string",
          "format": "date-time"
        },
        "date": {
          "type": "string",
          "format": "date"
        }
      }
    },
    "alternative": {
      "title": "Alternative",
      "description": "These work on every platform.",
      "type": "object",
      "properties": {
        "alt-datetime": {
          "type": "string",
          "format": "date-time"
        },
        "alt-date": {
          "type": "string",
          "format": "date"
        }
      }
    }
  }
}
"""

form1_data = json.dumps({
    'project': 'My first project',
    'something': True,
    'someNumber': 12345
})

master_user_id = 252L
form_id = 'form1'
form_schema = form1
ui_schema = ui1
group_ids = [203L]

# Add a form
# utils.add_form(conn, master_user_id, form_id, form_schema, ui_schema,
#                group_ids)

# List all the forms
# for form in utils.list_forms(conn, master_user_id):
#     pprint(form)

# List all the forms in a group
# for form in utils.list_forms(conn, master_user_id, 203L):
#     pprint(form)

# Get a form
# pprint(utils.get_form(conn, master_user_id, form_id))

# utils.delete_form(conn, master_user_id, form_id)

# Add data for a form
# utils.add_form_data(conn, master_user_id, form_id, 'Dataset', 251L,
#                     form1_data, 'rou', datetime.now())

# Get data for a form
# print 'Changed At\t\t', '\tChanged By', '\tForm Data'
# for form_data in utils.get_form_data_history(conn, master_user_id, form_id,
#                                              'Dataset', 251L):
#     # print(form_data)
#     print form_data['changed_at'], '\t', form_data['changed_by'], '\t\t',  form_data['form_data']

# Get latest data for a form
# pprint(utils.get_form_data(conn, master_user_id, form_id, 'Dataset', 251L))

# Delete data for a form
# utils.delete_form_data(conn, master_user_id, form_id, 'Dataset', 251L)

# utils.add_form_data_to_obj(conn, form_id, 'Dataset', 251L, form1_data)

# utils.delete_form_kvdata(conn, form_id, 'Dataset', 251L)

# utils._list_form_data_orphans(conn, master_user_id)

# import omero
# qs = conn.getQueryService()
#
# conn.SERVICE_OPTS.setOmeroGroup(203L)
#
# params = omero.sys.ParametersI()
# params.add('aid', omero.rtypes.wrap(long(422)))
#
# # Get all the annotations attached to the form master user
# q = """
#     SELECT anno
#     FROM MapAnnotation anno
#
#     """
#     # WHERE anno.id = :aid
# rows = qs.projection(q, params, conn.SERVICE_OPTS)
#
# for row in rows:
#     # anno = row[0].val
#
#     print row
#
#     # handle = conn.deleteObjects('MapAnnotation', [anno.id.val])
#     # cb = omero.callbacks.CmdCallbackI(conn.c, handle)
#     #
#     # while not cb.block(500):
#     #     pass
#     # err = isinstance(cb.getResponse(), omero.cmd.ERR)
#     # if err:
#     #     # TODO Throw exception
#     #     pass
#     #     # print cb.getResponse()
#     # cb.close(True)
