from omero_basics import OMEROConnectionManager
import omero
from copy import deepcopy

conn_manager = OMEROConnectionManager()
conn = conn_manager.connect()


def addForm(form, form_id, group_id):

    service_opts = deepcopy(conn.SERVICE_OPTS)
    service_opts.setOmeroGroup(group_id)

    # TODO As using direct save method, need to set the SERVICE_OPTS directly
    conn.SERVICE_OPTS.setOmeroGroup(group_id)

    # TODO Ensure that there is no other form with this ID?
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


def listAllMapAnnotations(group_id=-1):
    params = omero.sys.ParametersI()
    params.add('oname', omero.rtypes.wrap('formmaster'))
    service_opts = deepcopy(conn.SERVICE_OPTS)
    service_opts.setOmeroGroup(group_id)

    qs = conn.getQueryService()
    q = """
        SELECT anno
        FROM MapAnnotation anno
        JOIN anno.details details
        WHERE details.owner.omeName = :oname
        """

    for e in qs.projection(q, params, service_opts):
        anno = e[0].val
        for pair in anno.getMapValue():
            print('ID: %i Key: %s' % (anno.id.val, pair.name))
            print(pair.value)


def listAllMapAnnotationsOnDataset(dataset_id, group_id=-1):
    params = omero.sys.ParametersI()
    params.add('oname', omero.rtypes.wrap('formmaster'))
    params.add('did', omero.rtypes.wrap(long(dataset_id)))
    service_opts = deepcopy(conn.SERVICE_OPTS)
    service_opts.setOmeroGroup(group_id)

    qs = conn.getQueryService()
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

    for e in qs.projection(q, params, service_opts):
        anno = e[0].val
        for pair in anno.getMapValue():
            print('\tID: %i Key: %s - %s' % (anno.id.val, pair.name,
                                             pair.value))


def editForm(anno_id, form, group_id=-1):

    params = omero.sys.ParametersI()
    params.add('oname', omero.rtypes.wrap('formmaster'))
    params.add('aid', omero.rtypes.wrap(long(anno_id)))
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
        AND anno.id = :aid
        AND details.owner.omeName = :oname
        """

    rows = qs.projection(q, params, service_opts)
    assert len(rows) == 1

    form_json = None
    form_id = None

    if group_id == -1:
        service_opts.setOmeroGroup(rows[0][1].val.id.val)
    else:
        assert group_id == rows[0][1].val.id.val

    anno = rows[0][0].val
    for pair in anno.getMapValue():
        if pair.name == 'form_json':
            form_json = pair.value
        elif pair.name == 'form_id':
            form_id = pair.value

    assert form_json is not None
    assert form_id is not None

    keyValueData = [
        ["form_json", form],
        ["form_id", form_id]
    ]

    keyValueData = [omero.model.NamedValue(d[0], d[1]) for d in keyValueData]

    anno.setMapValue(keyValueData)

    us = conn.getUpdateService()
    us.saveObject(anno, service_opts)


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


def listGroups():
    params = omero.sys.ParametersI()
    service_opts = deepcopy(conn.SERVICE_OPTS)

    qs = conn.getQueryService()
    q = """
        SELECT grp
        FROM ExperimenterGroup grp
        """

    for e in qs.projection(q, params, service_opts):
        group = e[0].val
        print group.id.val, group.name.val


def addOther(dataset_id, group_id):
    service_opts = deepcopy(conn.SERVICE_OPTS)
    service_opts.setOmeroGroup(group_id)

    # TODO As using direct save method, need to set the SERVICE_OPTS directly
    conn.SERVICE_OPTS.setOmeroGroup(group_id)

    keyValueData = [["other6", "other6"]]
    mapAnn = omero.gateway.MapAnnotationWrapper(conn)
    # namespace = omero.constants.metadata.NSCLIENTMAPANNOTATION
    namespace = "dpwr"
    mapAnn.setNs(namespace)
    mapAnn.setValue(keyValueData)
    mapAnn.save()
    link = omero.model.DatasetAnnotationLinkI()
    link.parent = omero.model.DatasetI(dataset_id, False)
    link.child = mapAnn._obj
    update = conn.getUpdateService()
    update.saveObject(link, service_opts)


def deleteOther(anno_id):

    handle = conn.deleteObjects('MapAnnotation', [anno_id])
    cb = omero.callbacks.CmdCallbackI(conn.c, handle)
    print 'Deleting anno: %s' % anno_id
    while not cb.block(500):
        print "."
    err = isinstance(cb.getResponse(), omero.cmd.ERR)
    if err:
        print cb.getResponse()
    cb.close(True)


def getFormData(dataset_id, form_id, group_id=-1):

    service_opts = deepcopy(conn.SERVICE_OPTS)
    service_opts.setOmeroGroup(group_id)

    params = omero.sys.ParametersI()
    params.add('oname', omero.rtypes.wrap('formmaster'))
    params.add('did', omero.rtypes.wrap(long(dataset_id)))
    params.add('fid', omero.rtypes.wrap(form_id))


    qs = conn.getQueryService()
    q = """
        SELECT mapValue.value, anno
        FROM Dataset dataset
        JOIN dataset.annotationLinks links
        JOIN links.child anno
        JOIN anno.details details
        JOIN anno.mapValue mapValue
        WHERE anno.class = MapAnnotation
        AND dataset.id = :did
        AND details.owner.omeName = :oname
        AND mapValue.name = 'form_id'
        AND mapValue.value = :fid
        """

    rows = qs.projection(q, params, service_opts)

    for row in rows:
        mv = row[0]
        anno = row[1]
        print mv.val, '\t', anno.val.id.val


def datasetFormHistory(dataset_id, form_id, group_id):

    form_history_id = '%s_%s_%s' % ('Dataset', dataset_id, form_id)

    params = omero.sys.ParametersI()
    params.add('oname', omero.rtypes.wrap('formmaster'))
    params.add('gid', omero.rtypes.wrap(long(group_id)))
    params.add('fhid', omero.rtypes.wrap(form_history_id))
    service_opts = deepcopy(conn.SERVICE_OPTS)
    service_opts.setOmeroGroup(group_id)

    qs = conn.getQueryService()
    q = """
        SELECT anno
        FROM ExperimenterGroup grp
        JOIN grp.annotationLinks links
        JOIN links.child anno
        JOIN anno.details details
        JOIN anno.mapValue mapValue
        WHERE anno.class = MapAnnotation
        AND grp.id = :gid
        AND details.owner.omeName = :oname
        AND mapValue.name = 'form_history_id'
        AND mapValue.value = :fhid
        """

    rows = qs.projection(q, params, service_opts)
    assert len(rows) == 1

    anno = rows[0][0].val
    print 'Annotation %i' % anno.id.val
    for pair in anno.getMapValue():
        if pair.name == 'history':
            print('History: %s' % pair.value)

# Add a key-value to the group
form1 = """
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

# listForms()
# listForms(103)
# addForm(form1, "science_stuff1", 203)
# addForm(form2, "second_form", 203)
# deleteForm(420)
# listDatasets(103)
# listGroups()
# addOther(201, 103)
# editForm(412, form2)
# editForm(412, form2, 203)
listAllMapAnnotations()
# deleteOther(349)
# getFormData(251, "science_stuff1", 203)
# listAllMapAnnotationsOnDataset(201, 103)
# datasetFormHistory(201, 'science_stuff1', 103)

# for x in [340, 301, 329]:
    # deleteOther(x)
