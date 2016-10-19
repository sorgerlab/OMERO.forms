from django.http import (HttpResponse, HttpResponseNotAllowed,
                         HttpResponseBadRequest)

from omeroweb.webclient.decorators import login_required, render_response
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

import omero
from omero.rtypes import rstring, rlong, wrap, unwrap

from copy import deepcopy
from datetime import datetime

from omeroweb.webclient import tree

import json
import logging

logger = logging.getLogger(__name__)

from forms import settings
from forms import utils

OMERO_FORMS_PRIV_UID = None


def get_priv_uid(conn):
    global OMERO_FORMS_PRIV_UID
    if OMERO_FORMS_PRIV_UID is not None:
        return OMERO_FORMS_PRIV_UID

    qs = conn.getQueryService()

    params = omero.sys.ParametersI()
    params.add(
        'username',
        omero.rtypes.wrap(str(settings.OMERO_FORMS_PRIV_USER))
    )

    q = """
        SELECT user.id
        FROM Experimenter user
        WHERE user.omeName = :username
        """

    rows = qs.projection(q, params, conn.SERVICE_OPTS)
    assert len(rows) == 1

    OMERO_FORMS_PRIV_UID = rows[0][0].val
    return OMERO_FORMS_PRIV_UID


class HttpJsonResponse(HttpResponse):
    def __init__(self, content, cls=json.JSONEncoder.default):
        HttpResponse.__init__(
            self, json.dumps(content, cls=cls),
            content_type="application/json"
        )


@login_required(setGroupContext=True)
def update(request, conn=None, **kwargs):

    if request.method != 'POST':
        return HttpResponseNotAllowed('Methods allowed: POST')

    update_data = json.loads(request.body)

    form_id = update_data['formId']
    form_data = update_data['formData']
    obj_type = update_data['objType']
    obj_id = update_data['objId']
    changed_at = datetime.now()
    changed_by = conn.user.getName()

    group_id = request.session.get('active_group')
    if group_id is None:
        group_id = conn.getEventContext().groupId

    # Create a super user connection
    su_conn = conn.clone()
    su_conn.setIdentity(
        settings.OMERO_FORMS_PRIV_USER,
        settings.OMERO_FORMS_PRIV_PASSWORD
    )
    su_conn.connect()

    if not su_conn.connect():
        # TODO Throw Exception
        pass

    # TODO Check that the form submitted is valid for the group it is being
    # submitted for

    # TODO Check that the user is a member of the current group and that the
    # dataset is in that group

    utils.add_form_data(su_conn, get_priv_uid(conn), form_id,
                        obj_type, obj_id, form_data, changed_by, changed_at)

    utils.add_form_data_to_obj(conn, form_id, obj_type, obj_id, form_data)

    return HttpResponse('')


@login_required(setGroupContext=True)
def dataset_keys(request, conn=None, **kwargs):

    # TODO Indicate whether this user can populate the form.
    # Private group: Yes, if own data, which it always will be.
    # Read-only group: Yes, if owner. No, otherwise
    # Read-annotate group: Yes, always
    # Read-write group: Forms disabled

    if request.method != 'GET':
        return HttpResponseNotAllowed('Methods allowed: GET')

    obj_id = request.GET.get("objId")

    if not obj_id:
        return HttpResponseBadRequest('Object ID required')

    obj_id = long(obj_id)

    obj_type = request.GET.get("objType")

    if not obj_type:
        return HttpResponseBadRequest('Object type required')

    obj_types = ['Dataset', 'Project', 'Plate', 'Screen']
    if obj_type not in obj_types:
        return HttpResponseBadRequest(
            'Object type in ' + ','.join(obj_types) + ' required'
        )

    group_id = request.session.get('active_group')
    if group_id is None:
        group_id = conn.getEventContext().groupId

    # Set the desired group context
    # TODO Test when this takes hold if at all?
    # conn.SERVICE_OPTS.setOmeroGroup(group_id)

    su_conn = conn.clone()

    su_conn.setIdentity(
        settings.OMERO_FORMS_PRIV_USER,
        settings.OMERO_FORMS_PRIV_PASSWORD
    )

    if not su_conn.connect():
        # TODO Throw Exception
        pass

    forms = [
        {
            'formId': form['form_id'],
            'jsonSchema': form['json_schema'],
            'uiSchema': form['ui_schema'],
            'groupIds': form['group_ids'],
            'objTypes': form['obj_types']
        }
        for form
        in utils.list_forms(su_conn, get_priv_uid(conn), group_id, obj_type)
    ]

    # # TODO Handle this in a single query?
    for form in forms:
        form_data = utils.get_form_data(
            su_conn, get_priv_uid(conn), form['formId'],
            obj_type, obj_id
        )
        if form_data is not None:
            form['formData'] = form_data['form_data']

    return HttpJsonResponse(
        {
            'forms': forms
        },
        cls=utils.DatetimeEncoder
    )


@login_required(setGroupContext=True)
def designer(request, conn=None, **kwargs):
    context = {}
    return render(request, "forms/designer.html", context)


@login_required(setGroupContext=True)
def list_forms(request, conn=None, **kwargs):

    if request.method != 'GET':
        return HttpResponseNotAllowed('Methods allowed: GET')

    # Create a super user connection
    su_conn = conn.clone()
    su_conn.setIdentity(
        settings.OMERO_FORMS_PRIV_USER,
        settings.OMERO_FORMS_PRIV_PASSWORD
    )
    su_conn.connect()

    if not su_conn.connect():
        # TODO Throw Exception
        pass

    # TODO Should only return groupIds for groups that this user can
    # assign
    forms = [
        {
            'formId': form['form_id'],
            'jsonSchema': form['json_schema'],
            'uiSchema': form['ui_schema'],
            'groupIds': form['group_ids'],
            'objTypes': form['obj_types']
        }
        for form
        in utils.list_forms(su_conn, get_priv_uid(conn))
    ]

    return HttpJsonResponse(
        {
            'forms': forms
        },
        cls=utils.DatetimeEncoder
    )


@login_required(setGroupContext=True)
@csrf_exempt
def add_form(request, conn=None, **kwargs):

    if request.method != 'POST' and request.method != 'PUT':
        return HttpResponseNotAllowed('Methods allowed: POST, PUT')

    # Create a super user connection
    su_conn = conn.clone()
    su_conn.setIdentity(
        settings.OMERO_FORMS_PRIV_USER,
        settings.OMERO_FORMS_PRIV_PASSWORD
    )
    su_conn.connect()

    if not su_conn.connect():
        # TODO Throw Exception
        pass

    data = json.loads(request.body)
    form_id = data.get('formId')
    schema = data.get('jsonSchema', '')
    ui_schema = data.get('uiSchema', '')
    obj_types = data.get('objTypes', [])

    # Ensure there is at least a formId
    if form_id is None:
        return HttpResponseBadRequest(
            'Adding or updating a form requires a formId to be specified'
        )

    # Ensure the object type is valid
    for obj_type in obj_types:
        assert obj_type in ['Project', 'Dataset', 'Screen', 'Plate']

    existing_form = utils.get_form(su_conn, get_priv_uid(conn), form_id)

    group_ids = []
    if existing_form is not None:
        # TODO Check if the current user has the rights to overwrite this form
        print existing_form
        group_ids = existing_form['group_ids']


    utils.add_form(su_conn, get_priv_uid(conn), form_id, schema,
                   ui_schema, group_ids=group_ids, obj_types=obj_types,
                   replace=True)

    return HttpJsonResponse({}, cls=utils.DatetimeEncoder)


@login_required(setGroupContext=True)
@csrf_exempt
def assign_form(request, conn=None, **kwargs):

    if request.method != 'POST':
        return HttpResponseNotAllowed('Methods allowed: POST')

    # Create a super user connection
    su_conn = conn.clone()
    su_conn.setIdentity(
        settings.OMERO_FORMS_PRIV_USER,
        settings.OMERO_FORMS_PRIV_PASSWORD
    )
    su_conn.connect()

    if not su_conn.connect():
        # TODO Throw Exception
        pass

    data = json.loads(request.body)

    form_id = data['formId']
    group_ids = data['groupIds']

    existing_form = utils.get_form(su_conn, get_priv_uid(conn), form_id)

    assert existing_form is not None

    utils.add_form(
        su_conn,
        get_priv_uid(conn),
        form_id,
        existing_form['json_schema'],
        existing_form['ui_schema'],
        group_ids,
        existing_form['obj_types'],
        True
    )

    return HttpJsonResponse({}, cls=utils.DatetimeEncoder)


@login_required(setGroupContext=True)
def managed_groups(request, conn=None, **kwargs):

    return HttpJsonResponse({
        'groups': utils.get_managed_groups(conn)
    }, cls=utils.DatetimeEncoder)


@login_required(setGroupContext=True)
def form_data(request, form_id, obj_type, obj_id, conn=None, **kwargs):
    print 'form_data'
    print request

    # Create a super user connection
    su_conn = conn.clone()
    su_conn.setIdentity(
        settings.OMERO_FORMS_PRIV_USER,
        settings.OMERO_FORMS_PRIV_PASSWORD
    )
    su_conn.connect()

    if not su_conn.connect():
        # TODO Throw Exception
        pass

    form_data = utils.get_form_data_history(
        su_conn,
        get_priv_uid(conn),
        form_id,
        obj_type,
        obj_id
    )

    x = [f for f in form_data]
    print x

    return HttpJsonResponse({
        'formData': x
    }, cls=utils.DatetimeEncoder)
