from django.http import (HttpResponse, HttpResponseNotAllowed,
                         HttpResponseBadRequest)

from omeroweb.webclient.decorators import login_required, render_response
from omeroweb.http import HttpJsonResponse

import omero
from omero.rtypes import rstring, rlong, wrap, unwrap

from copy import deepcopy

from omeroweb.webclient import tree

import json
import logging

logger = logging.getLogger(__name__)

from . import settings

@login_required(setGroupContext=True)
def update(request, conn=None, **kwargs):

    if not request.POST:
        return HttpResponseNotAllowed('Methods allowed: POST')

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
        for pair in anno.getMapValue():
            if pair.name == 'form_json':
                forms.append(pair.value)

    print forms

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
