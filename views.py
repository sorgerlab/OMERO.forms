from django.http import (HttpResponse, HttpResponseNotAllowed,
                         HttpResponseBadRequest)

from omeroweb.webclient.decorators import login_required, render_response
from omeroweb.http import HttpJsonResponse

import omero
from omero.rtypes import rstring, rlong, wrap, unwrap

from utils import createTagAnnotationsLinks

from copy import deepcopy

from omeroweb.webclient import tree

import json
import logging

logger = logging.getLogger(__name__)


@login_required(setGroupContext=True)
def process_update(request, conn=None, **kwargs):

    if not request.POST:
        return HttpResponseNotAllowed('Methods allowed: POST')

    images = json.loads(request.body)

    additions = []
    removals = []

    for image in images:
        image_id = image['imageId']

        additions.extend(
            [
                (long(image_id), long(addition),)
                for addition in image['additions']
            ]
        )

        removals.extend(
            [
                (long(image_id), long(removal),)
                for removal in image['removals']
            ]
        )

    # TODO Interface for createTagAnnotationsLinks is a bit nasty, but go
    # along with it for now
    createTagAnnotationsLinks(conn, additions, removals)

    return HttpResponse('')

# def _marshal_image(conn, row, tags_on_images):
#     image = tree._marshal_image(conn, row[0:5])
#     image['clientPath'] = unwrap(row[5])
#     image['tags'] = tags_on_images.get(image['id']) or []
#     return image

@login_required(setGroupContext=True)
def main(request, conn=None, **kwargs):

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

    qs = conn.getQueryService()

    # Get the key-values that are applied to this dataset
    q = """
        SELECT anno
        FROM Dataset dataset
        JOIN dataset.annotationLinks links
        JOIN links.child anno
        WHERE anno.class = MapAnnotation
        AND dataset.id = :did
        """

    annotations = []
    for e in qs.projection(q, params, service_opts):
        anno = e[0]
        kvs = {}
        for pair in anno.getMapValue():
            print '\t%s = %s' % (pair.name, pair.value)
            kvs[pair.name] = pair.value
        annotations.append(kvs)

    return HttpJsonResponse(
        {
            'annotations': annotations
        }
    )
