from omero_basics import OMEROConnectionManager
import omero
from copy import deepcopy

conn_manager = OMEROConnectionManager()
conn = conn_manager.connect()

def addForm(form, form_id, group_id):
    service_opts = deepcopy(conn.SERVICE_OPTS)
    service_opts.setOmeroGroup(group_id)
    keyValueData = [
        ["form_json", form],
        ["form_id", form_id]
    ]
    mapAnn = omero.gateway.MapAnnotationWrapper(conn)
    namespace = omero.constants.metadata.NSCLIENTMAPANNOTATION
    mapAnn.setNs(namespace)
    mapAnn.setValue(keyValueData)
    mapAnn.save()
    link = omero.model.ExperimenterGroupAnnotationLinkI()
    link.parent = omero.model.ExperimenterGroupI(group_id, False)
    link.child = mapAnn._obj
    update = conn.getUpdateService()
    update.saveObject(link, service_opts)


def deleteForm(anno_id):

    handle = conn.deleteObjects('MapAnnotation', [anno_id])
    cb = omero.callbacks.CmdCallbackI(conn.c, handle)
    print 'Deleting anno: %s' % anno_id
    while not cb.block(500):
        print "."
    err = isinstance(cb.getResponse(), omero.cmd.ERR)
    if err:
        print cb.getResponse()
    cb.close(True)


def listForms(group_id=-1):
    params = omero.sys.ParametersI()
    params.add('oname', omero.rtypes.wrap('formmaster'))
    service_opts = deepcopy(conn.SERVICE_OPTS)
    service_opts.setOmeroGroup(group_id)

    qs = conn.getQueryService()
    q = """
        SELECT anno, grp
        FROM ExperimenterGroup grp
        JOIN grp.annotationLinks links
        JOIN links.child anno
        JOIN anno.details details
        WHERE anno.class = MapAnnotation
        AND details.owner.omeName = :oname
        """

    for e in qs.projection(q, params, service_opts):
        anno = e[0].val
        group = e[1].val
        for pair in anno.getMapValue():
            if pair.name == 'form_json':
                print('Annotation: %i (Group: %i)' % (anno.id.val, group.id.val))
                print(pair.value)
            elif pair.name == 'form_id':
                print('Form name')
                print(pair.value)


def editForm(anno_id, group_id=-1):
    anno = conn.getObject('MapAnnotation', anno_id)
    print anno

def listDatasets(group_id=-1):
    params = omero.sys.ParametersI()
    params.add('oname', omero.rtypes.wrap('formmaster'))
    service_opts = deepcopy(conn.SERVICE_OPTS)
    service_opts.setOmeroGroup(group_id)

    qs = conn.getQueryService()
    q = """
        SELECT anno, dataset
        FROM Dataset dataset
        JOIN dataset.annotationLinks links
        JOIN links.child anno
        JOIN anno.details details
        WHERE anno.class = MapAnnotation
        AND details.owner.omeName = :oname
        """

    for e in qs.projection(q, params, service_opts):
        anno = e[0].val
        dataset = e[1].val
        for pair in anno.getMapValue():
            # if pair.name == 'form_json':
            print('Dataset: %i' % dataset.id.val)
            print(pair.name)
            print(pair.value)


def listGroups(group_id=-1):
    params = omero.sys.ParametersI()
    service_opts = deepcopy(conn.SERVICE_OPTS)
    service_opts.setOmeroGroup(group_id)

    qs = conn.getQueryService()
    q = """
        SELECT grp
        FROM ExperimenterGroup grp
        """

    for e in qs.projection(q, params, service_opts):
        group = e[0].val
        print group.id.val

def addOther(dataset_id, group_id):
    service_opts = deepcopy(conn.SERVICE_OPTS)
    service_opts.setOmeroGroup(group_id)
    keyValueData = [["other1", "other1"]]
    mapAnn = omero.gateway.MapAnnotationWrapper(conn)
    namespace = omero.constants.metadata.NSCLIENTMAPANNOTATION
    mapAnn.setNs(namespace)
    mapAnn.setValue(keyValueData)
    mapAnn.save()
    link = omero.model.DatasetAnnotationLinkI()
    link.parent = omero.model.DatasetI(dataset_id, False)
    link.child = mapAnn._obj
    update = conn.getUpdateService()
    update.saveObject(link, service_opts)

# Add a key-value to the group
form = """
{
    "title": "Science stuff",
    "type": "object",
    "required": ["project", "someNumber"],
    "properties": {
      "project": {"type": "string", "title": "Project"},
      "something": {"type": "boolean", "title": "Something?", "default": false},
      "someNumber": {"type": "number", "title": "Some number"}
    }
}
"""

# listForms()
# listForms(103)
# addForm(form, "science_stuff1", 103)
# deleteForm(345)
# listDatasets(103)
# listGroups()
# addOther(201, 103)
editForm(346, 103)
