from django.http import (HttpResponse, HttpResponseNotAllowed,
                         HttpResponseBadRequest)

from omeroweb.webclient.decorators import login_required, render_response
from omeroweb.http import HttpJsonResponse

import omero
from omero.rtypes import rstring, rlong, wrap, unwrap

from copy import deepcopy
import datetime

from omeroweb.webclient import tree

import json
import logging

logger = logging.getLogger(__name__)

from . import settings
from . import utils

@login_required(setGroupContext=True)
def update(request, conn=None, **kwargs):

    if not request.POST:
        return HttpResponseNotAllowed('Methods allowed: POST')

    update_data = json.loads(request.body)

    print update_data

    form_id = update_data['formId']
    form_data = update_data['formData']
    object_type = "Dataset"
    object_id = update_data['datasetId']
    changed_at = datetime.datetime.now()
    user_id = conn.user.getName()


    group_id = request.session.get('active_group')
    if group_id is None:
        group_id = conn.getEventContext().groupId

    # print form_id
    # print form_data
    # print changed_at
    # print user_id
    # print group_id

    # print type(form_data)

    # Create a super user connection
    su_conn = conn.clone()
    su_conn.setIdentity(
        settings.OMERO_FORMS_PRIV_USER,
        settings.OMERO_FORMS_PRIV_PASSWORD
    )
    su_conn.connect()

    # TODO Check that the form submitted is valid for the group it is being
    # submitted for

    # TODO Check that the user is a member of the current group and that the
    # dataset is in that group

    # Set the group to the current group
    su_conn.SERVICE_OPTS.setOmeroGroup(group_id)

    utils.addOrUpdateObjectMapAnnotation(su_conn, object_type, object_id,
                                         form_id, form_data)


    # TODO Save the JSON form data to the history location, wherever that is
    #   json-data
    #   timestamp of change
    #   author of change
    utils.addOrUpdateHistoryMapAnnotation(su_conn, object_type, object_id,
                                          form_id, form_data, user_id)



    # images = json.loads(request.body)
    #
    # additions = []
    # removals = []
    #
    # for image in images:
    #     image_id = image['imageId']
    #
    #     additions.extend(
    #         [
    #             (long(image_id), long(addition),)
    #             for addition in image['additions']
    #         ]
    #     )
    #
    #     removals.extend(
    #         [
    #             (long(image_id), long(removal),)
    #             for removal in image['removals']
    #         ]
    #     )
    #
    # # TODO Interface for createTagAnnotationsLinks is a bit nasty, but go
    # # along with it for now
    # createTagAnnotationsLinks(conn, additions, removals)

    return HttpResponse('')

# def _marshal_image(conn, row, tags_on_images):
#     image = tree._marshal_image(conn, row[0:5])
#     image['clientPath'] = unwrap(row[5])
#     image['tags'] = tags_on_images.get(image['id']) or []
#     return image

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

    # Details about the annotations specified
    params = omero.sys.ParametersI()
    service_opts = deepcopy(conn.SERVICE_OPTS)

    # Set the desired group context
    service_opts.setOmeroGroup(group_id)

    params.add('did', wrap(dataset_id))
    # params.add('gid', wrap(group_id))
    params.add('oname', wrap(settings.OMERO_FORMS_PRIV_USER))

    qs = conn.getQueryService()

    # Get the key-values that are applied to this dataset by the form master
    q = """
        SELECT anno
        FROM Dataset dataset
        JOIN dataset.annotationLinks links
        JOIN links.child anno
        JOIN anno.details details
        WHERE anno.class = MapAnnotation
        AND dataset.id = :did
        AND details.owner.omeName = :oname
        """
# JOIN anno.mapValue mapValues
# AND mapValues.name = 'group_form'

    annotations = []
    for e in qs.projection(q, params, service_opts):
        anno = e[0].val
        kvs = {}
        for pair in anno.getMapValue():
            # print '\t%s = %s' % (pair.name, pair.value)
            kvs[pair.name] = pair.value
        annotations.append(kvs)

    # Get the forms available to users of this group
    q = """
        SELECT anno
        FROM ExperimenterGroup grp
        JOIN grp.annotationLinks links
        JOIN links.child anno
        JOIN anno.details details
        WHERE anno.class = MapAnnotation
        AND details.owner.omeName = :oname
        """
        # JOIN anno.mapValue mapValues
        # AND mapValues.name = 'form_json'

    forms = []
    for e in qs.projection(q, params, service_opts):
        anno = e[0].val
        form_json = None
        form_id = None
        for pair in anno.getMapValue():
            if pair.name == 'form_json':
                form_json = pair.value
            if pair.name == 'form_id':
                form_id = pair.value

        if form_json is not None and form_id is not None:
            forms.append({
                'form_id': form_id,
                'form_json': form_json
            })

    print forms

    # TODO Handle this in a single query, also without having to iterate pairs
    for form in forms:
        anno = utils.getFormData(conn, 'Dataset', dataset_id, form['form_id'])

        if anno:
            for pair in anno.getMapValue():
                if pair.name == 'form_json':
                    form['form_data'] = pair.value
                    print 'found form data'
                    break

    # for e in qs.projection(q, params, service_opts):
    #     if

    # form = """
    # {
    #     "title": "Science stuff",
    #     "type": "object",
    #     "required": ["project", "someNumber"],
    #     "properties": {
    #       "project": {"type": "string", "title": "Project"},
    #       "something": {"type": "boolean", "title": "Something?", "default": false},
    #       "someNumber": {"type": "number", "title": "Some number"}
    #     }
    # }
    # """
    #
    # forms = [form]

    # print('User is: %s' % settings.OMERO_FORMS_PRIV_USER)
    # print('Password is: %s' % settings.OMERO_FORMS_PRIV_PASSWORD)

    # Test: Create a super user connection
    # su_conn = conn.clone()
    # su_conn.setIdentity(
    #     settings.OMERO_FORMS_PRIV_USER,
    #     settings.OMERO_FORMS_PRIV_PASSWORD
    # )
    # if not su_conn.connect():
    #     print('Not Connected')
    #check su function

    return HttpJsonResponse(
        {
            'annotations': annotations,
            'forms': forms
        }
    )
