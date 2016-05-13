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


@login_required(setGroupContext=True)
def create_tag(request, conn=None, **kwargs):
    """
    Creates a Tag from POST data.
    """

    if not request.POST:
        return HttpResponseNotAllowed('Methods allowed: POST')

    tag = json.loads(request.body)

    tag_value = tag['value']
    tag_description = tag['description']

    tag = omero.model.TagAnnotationI()
    tag.textValue = rstring(str(tag_value))
    if tag_description is not None:
        tag.description = rstring(str(tag_description))

    tag = conn.getUpdateService().saveAndReturnObject(tag, conn.SERVICE_OPTS)

    params = omero.sys.ParametersI()
    service_opts = deepcopy(conn.SERVICE_OPTS)

    qs = conn.getQueryService()

    q = '''
        select new map(tag.id as id,
               tag.textValue as textValue,
               tag.description as description,
               tag.details.owner.id as ownerId,
               tag as tag_details_permissions,
               tag.ns as ns,
               (select count(aalink2)
                from AnnotationAnnotationLink aalink2
                where aalink2.child.class=TagAnnotation
                and aalink2.parent.id=tag.id) as childCount)
        from TagAnnotation tag
        where tag.id = :tid
        '''

    params.add('tid', rlong(tag.id))

    e = qs.projection(q, params, service_opts)[0]
    e = unwrap(e)
    e = [e[0]["id"],
         e[0]["textValue"],
         e[0]["description"],
         e[0]["ownerId"],
         e[0]["tag_details_permissions"],
         e[0]["ns"],
         e[0]["childCount"]]

    tag = tree._marshal_tag(conn, e)

    return HttpJsonResponse(
        tag
    )


def _marshal_image(conn, row, tags_on_images):
    image = tree._marshal_image(conn, row[0:5])
    image['clientPath'] = unwrap(row[5])
    image['tags'] = tags_on_images.get(image['id']) or []
    return image

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

    # Details about the images specified
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

    kvs = {}
    for e in qs.projection(q, params, service_opts):
        anno = e[0]
        for pair in anno.getMapValue():
            print '\t%s = %s' % (pair.name, pair.value)
            kvs[pair.name] = pair.value

    return HttpJsonResponse(
        {
            'kvs': kvs
        }
    )
