import omero
import json
from . import settings


def addOrUpdateObjectMapAnnotation(conn, object_type, object_id, form_id,
                                   form_data):

    keyValueData = [[str(key), str(value)] for key, value in form_data.iteritems()]
    keyValueData.append(['form_id', form_id])
    keyValueData.append(['form_json', json.dumps(form_data)])

    import pprint
    pprint.pprint(keyValueData)

    # If the appropriate annotation already exists, update it
    anno = getFormData(conn, object_type, object_id, form_id)
    if anno:
        print anno
        anno.setMapValue(
            [omero.model.NamedValue(d[0], d[1]) for d in keyValueData]
        )
        us = conn.getUpdateService()
        us.saveObject(anno, conn.SERVICE_OPTS)

    # If it does not already exist, create a new one
    else:

        mapAnn = omero.gateway.MapAnnotationWrapper(conn)
        namespace = omero.constants.metadata.NSCLIENTMAPANNOTATION

        mapAnn.setNs(namespace)
        mapAnn.setValue(keyValueData)
        mapAnn.save()

        if object_type == 'Dataset':

            link = omero.model.DatasetAnnotationLinkI()
            link.parent = omero.model.DatasetI(object_id, False)
        link.child = mapAnn._obj

        update = conn.getUpdateService()
        update.saveObject(link, conn.SERVICE_OPTS)


def getFormData(conn, object_type, object_id, form_id):

        params = omero.sys.ParametersI()
        params.add('oname', omero.rtypes.wrap(settings.OMERO_FORMS_PRIV_USER))
        params.add('oid', omero.rtypes.wrap(long(object_id)))
        params.add('fid', omero.rtypes.wrap(form_id))

        qs = conn.getQueryService()
        q = """
            SELECT anno
            FROM Dataset dataset
            JOIN dataset.annotationLinks links
            JOIN links.child anno
            JOIN anno.details details
            JOIN anno.mapValue mapValue
            WHERE anno.class = MapAnnotation
            AND dataset.id = :oid
            AND details.owner.omeName = :oname
            AND mapValue.name = 'form_id'
            AND mapValue.value = :fid
            """

        rows = qs.projection(q, params, conn.SERVICE_OPTS)

        if len(rows) == 1:
            return rows[0][0].val

        return False
