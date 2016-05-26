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
      "project": {"type": "string", "title": "Project"},
      "something": {"type": "boolean", "title": "Something?", "default": false},
      "someNumber": {"type": "number", "title": "Some number"}
    }
}
"""

form2 = """
{
    "title": "Second form",
    "type": "object",
    "required": ["project"],
    "properties": {
      "project": {"type": "string", "title": "Project2"}
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
group_ids = [203L]

# Add a form
# utils.add_form(conn, master_user_id, form_id, form_schema, group_ids)

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
# for form_data in utils.get_form_data_history(conn, master_user_id, form_id,
#                                              'Dataset', 251L):
#     print(form_data)

# Get latest data for a form
# pprint(utils.get_form_data(conn, master_user_id, form_id, 'Dataset', 251L))

# Delete data for a form
# utils.delete_form_data(conn, master_user_id, form_id, 'Dataset', 251L)

utils.add_form_data_to_obj(conn, form_id, 'Dataset', 251L, form1_data)
