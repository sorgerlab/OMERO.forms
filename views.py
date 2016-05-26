from django.http import (HttpResponse, HttpResponseNotAllowed,
                         HttpResponseBadRequest)

from omeroweb.webclient.decorators import login_required, render_response
from django.http import HttpResponse

import omero
from omero.rtypes import rstring, rlong, wrap, unwrap

from copy import deepcopy
from datetime import datetime

from omeroweb.webclient import tree

import json
import logging

logger = logging.getLogger(__name__)

from . import settings
from . import utils


class HttpJsonResponse(HttpResponse):
    def __init__(self, content, cls=json.JSONEncoder.default):
        HttpResponse.__init__(
            self, json.dumps(content, cls=cls),
            content_type="application/json"
        )


@login_required(setGroupContext=True)
def update(request, conn=None, **kwargs):

    if not request.POST:
        return HttpResponseNotAllowed('Methods allowed: POST')

    update_data = json.loads(request.body)

    form_id = update_data['formId']
    form_data = update_data['formData']
    obj_type = 'Dataset'
    obj_id = update_data['datasetId']
    changed_at = datetime.now()
    changed_by = conn.user.getName()

    group_id = request.session.get('active_group')
    if group_id is None:
        group_id = conn.getEventContext().groupId

    # Create a super user connection
    su_conn = conn.clone()
    # TODO Unhardcode this!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    su_conn.setIdentity(
        # settings.OMERO_FORMS_PRIV_USER,
        'formmaster',
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

    utils.add_form_data(su_conn, settings.OMERO_FORMS_PRIV_UID, form_id,
                        obj_type, obj_id, form_data, changed_by, changed_at)

    print type(form_data)

    utils.add_form_data_to_obj(conn, form_id, obj_type, obj_id, form_data)

    return HttpResponse('')


@login_required(setGroupContext=True)
def dataset_keys(request, conn=None, **kwargs):

    # TODO Indicate whether this user can populate the form.
    # Private group: Yes, if own data, which it always will be.
    # Read-only group: Yes, if owner. No, otherwise
    # Read-annotate group: Yes, always
    # Read-write group: Forms disabled

    if not request.GET:
        return HttpResponseNotAllowed('Methods allowed: GET')

    dataset_id = request.GET.get("datasetId")

    if not dataset_id:
        return HttpResponseBadRequest('Dataset ID required')

    dataset_id = long(dataset_id)

    group_id = request.session.get('active_group')
    if group_id is None:
        group_id = conn.getEventContext().groupId

    # Set the desired group context
    # TODO Test when this takes hold if at all?
    # conn.SERVICE_OPTS.setOmeroGroup(group_id)

    su_conn = conn.clone()

    # TODO Unhardcode this!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    su_conn.setIdentity(
        # settings.OMERO_FORMS_PRIV_UID,
        'formmaster',
        settings.OMERO_FORMS_PRIV_PASSWORD
    )

    if not su_conn.connect():
        # TODO Throw Exception
        pass

    forms = [
        {
            'formId': form['form_id'],
            'formSchema': form['form_schema'],
            'groupIds': form['group_ids']
        }
        for form
        in utils.list_forms(su_conn, settings.OMERO_FORMS_PRIV_UID, group_id)
    ]

    # # TODO Handle this in a single query?
    for form in forms:
        form_data = utils.get_form_data(
            su_conn, settings.OMERO_FORMS_PRIV_UID, form['formId'],
            'Dataset', dataset_id
        )
        if form_data is not None:
            form['formData'] = form_data['form_data']

    return HttpJsonResponse(
        {
            'forms': forms
        },
        cls=utils.DatetimeEncoder
    )
