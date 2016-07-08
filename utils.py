from functools import wraps
import omero
import json
from datetime import datetime
import re

# def as_form_master(f):
#     @wraps(f)
#     def wrapper(*args, **kwargs):
#         print args
#         print kwargs
#         return f(*args, **kwargs)
#     return wrapper


class DatetimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)


def get_formmaster_id(conn, formmaster_username):

    qs = conn.getQueryService()
    params = omero.sys.ParametersI()
    params.add('fm', omero.rtypes.wrap(formmaster_username))

    q = """
        SELECT user.id
        FROM Experimenter user
        WHERE user.omeName = :fm
        """

    rows = qs.projection(q, params, conn.SERVICE_OPTS)
    if len(rows) != 1:
        # TODO Raise exception instead
        print('user \'%s\' does not exists' % formmaster_username)

    return rows[0][0].val


def add_form(conn, master_user_id, form_id, json_schema, ui_schema,
             group_ids=[], obj_types=[]):
    """
    Add a form to the form master user and mark it for use in the designated
    groups.

    form_id must be globally unique
    """

    # TODO Validate schemas??

    qs = conn.getQueryService()

    namespace = 'hms.harvard.edu/omero/forms/schema/%s' % (form_id)
    params = omero.sys.ParametersI()
    params.add('mid', omero.rtypes.wrap(long(master_user_id)))
    params.add('ns', omero.rtypes.wrap(namespace))

    # Ensure that there is no other form with this ID
    q = """
        SELECT anno
        FROM Experimenter user
        JOIN user.annotationLinks links
        JOIN links.child anno
        WHERE anno.class = MapAnnotation
        AND user.id = :mid
        AND anno.ns = :ns
        """

    rows = qs.projection(q, params, conn.SERVICE_OPTS)
    if len(rows) != 0:
        # TODO Raise exception instead
        print('form id exists, please choose a unique form id')
        exit(1)

    # Add the form

    # Basic form data
    keyValueData = [
        ["json_schema", json_schema],
        ["ui_schema", ui_schema],
        ["form_id", form_id]
    ]

    # The groups that are subscribed to this form
    keyValueData.extend([['group', str(group_id)] for group_id in group_ids])

    # The object types that this form is intended for
    keyValueData.extend(
        [['obj_type', str(obj_type)] for obj_type in obj_types]
    )

    # Create and save the map annotation with the custom namespace and
    # specified key value data
    mapAnn = omero.gateway.MapAnnotationWrapper(conn)
    namespace = namespace
    mapAnn.setNs(namespace)
    mapAnn.setValue(keyValueData)
    mapAnn.save()

    # Link the map annotation to the form master user
    link = omero.model.ExperimenterAnnotationLinkI()
    link.parent = omero.model.ExperimenterI(master_user_id, False)
    link.child = mapAnn._obj
    update = conn.getUpdateService()
    update.saveObject(link, conn.SERVICE_OPTS)


def list_forms(conn, master_user_id, group_id=None, obj_type=None):
    """
    List all the forms, optionally limited to those available for a single
    group, and optionall limited to those available for a single object type
    """

    qs = conn.getQueryService()

    namespace = 'hms.harvard.edu/omero/forms/schema/%'
    params = omero.sys.ParametersI()
    params.add('mid', omero.rtypes.wrap(long(master_user_id)))
    params.add('ns', omero.rtypes.wrap(namespace))

    # Get all the annotations attached to the form master user
    q = """
        SELECT anno
        FROM Experimenter user
        JOIN user.annotationLinks links
        JOIN links.child anno
        WHERE anno.class = MapAnnotation
        AND user.id = :mid
        AND anno.ns LIKE :ns
        """

    # If group_id is specified, use a different query to restrict by that
    # group only
    if group_id is not None:
        params.add('gid', omero.rtypes.wrap(str(group_id)))
        q = """
            SELECT anno
            FROM Experimenter user
            JOIN user.annotationLinks links
            JOIN links.child anno
            JOIN anno.mapValue mapValue
            WHERE anno.class = MapAnnotation
            AND user.id = :mid
            AND anno.ns LIKE :ns
            AND mapValue.name = 'group'
            AND mapValue.value = :gid
            """

    rows = qs.projection(q, params, conn.SERVICE_OPTS)
    for row in rows:

        _form_id = None
        _json_schema = None
        _ui_schema = None
        _group_ids = []
        _obj_types = []

        anno = row[0].val
        kvs = anno.getMapValue()
        for kv in kvs:
            if kv.name == 'form_id':
                _form_id = kv.value
            elif kv.name == 'json_schema':
                _json_schema = kv.value
            elif kv.name == 'ui_schema':
                _ui_schema = kv.value
            elif kv.name == 'group':
                _group_ids.append(long(kv.value))
            elif kv.name == 'obj_type':
                _obj_types.append(kv.value)

        # TODO Throw exception
        assert _form_id is not None
        assert _json_schema is not None
        assert _ui_schema is not None

        # TODO Ideally this would be a part of the query, but it is easier to
        # simply filter here for now
        if obj_type is None or obj_type in _obj_types:

            yield {
                'form_id': _form_id,
                'json_schema': _json_schema,
                'ui_schema': _ui_schema,
                'group_ids': _group_ids,
                'obj_types': _obj_types
            }


def _get_form(conn, master_user_id, form_id):
    """
    Get a particular form

    Returns a MapAnnotationI object or None
    """

    qs = conn.getQueryService()

    namespace = 'hms.harvard.edu/omero/forms/schema/%s' % form_id
    params = omero.sys.ParametersI()
    params.add('mid', omero.rtypes.wrap(long(master_user_id)))
    params.add('ns', omero.rtypes.wrap(namespace))

    # Get all the annotations attached to the form master user
    q = """
        SELECT anno
        FROM Experimenter user
        JOIN user.annotationLinks links
        JOIN links.child anno
        WHERE anno.class = MapAnnotation
        AND user.id = :mid
        AND anno.ns = :ns
        """

    rows = qs.projection(q, params, conn.SERVICE_OPTS)

    # TODO Throw Exception
    assert len(rows) <= 1

    if len(rows) == 0:
        return None

    return rows[0][0].val


def get_form(conn, master_user_id, form_id):
    """
    Get a particular form
    """

    anno = _get_form(conn, master_user_id, form_id)

    if anno is None:
        return None

    _form_id = None
    _json_schema = None
    _ui_schema = None
    _group_ids = []
    _obj_types = []


    kvs = anno.getMapValue()
    for kv in kvs:
        if kv.name == 'form_id':
            _form_id = kv.value
        elif kv.name == 'json_schema':
            _json_schema = kv.value
        elif kv.name == 'ui_schema':
            _ui_schema = kv.value
        elif kv.name == 'group':
            _group_ids.append(long(kv.value))
        elif kv.name == 'obj_type':
            _obj_types.append(kv.value)

    # TODO Throw exception
    assert _form_id is not None
    assert _json_schema is not None
    assert _ui_schema is not None
    assert _form_id == form_id

    return {
        'form_id': _form_id,
        'json_schema': _json_schema,
        'ui_schema': _ui_schema,
        'group_ids': _group_ids,
        'obj_types': _obj_types
    }


def delete_form(conn, master_user_id, form_id):
    """
    Delete a form from the form master user.

    Does NOT delete any form data annotations which might relate to this
    """

    anno = _get_form(conn, master_user_id, form_id)

    handle = conn.deleteObjects('MapAnnotation', [anno.id.val])
    cb = omero.callbacks.CmdCallbackI(conn.c, handle)

    while not cb.block(500):
        pass
    err = isinstance(cb.getResponse(), omero.cmd.ERR)
    if err:
        # TODO Throw exception
        pass
        # print cb.getResponse()
    cb.close(True)


def _make_form_data_json(form_id, obj_type, obj_id, data, changed_by,
                         changed_at):
    """
    Build a json string containing the submitted form data, form_id, author
    of the changes and time at which the change was made
    """

    return json.dumps({
        'formId': form_id,
        'formData': data,
        'changedBy': changed_by,
        'changedAt': changed_at.isoformat()
    })


def _unmake_form_data_json(json_data):
    """
    Deconstruct the json string containing the submitted form data, form_id,
    author of the changes and time at which the change was made
    """

    loaded_data = json.loads(json_data)

    return {
        'form_id': loaded_data['formId'],
        'form_data': loaded_data['formData'],
        'changed_by': loaded_data['changedBy'],
        'changed_at': datetime.strptime(loaded_data['changedAt'],
                                        '%Y-%m-%dT%H:%M:%S.%f')
    }


def _get_form_data(conn, master_user_id, form_id, obj_type, obj_id):
    """
    Get the form data associated with a particular form for a particular
    object.

    Returns a MapAnnotationI object or None
    """

    namespace = 'hms.harvard.edu/omero/forms/data/%s%s/%s' % (
        obj_type,
        obj_id,
        form_id
    )

    params = omero.sys.ParametersI()
    params.add('mid', omero.rtypes.wrap(long(master_user_id)))
    params.add('ns', omero.rtypes.wrap(namespace))

    qs = conn.getQueryService()
    q = """
        SELECT anno
        FROM Experimenter user
        JOIN user.annotationLinks links
        JOIN links.child anno
        WHERE anno.class = MapAnnotation
        AND user.id = :mid
        AND anno.ns = :ns
        """

    rows = qs.projection(q, params, conn.SERVICE_OPTS)

    # TODO Throw Exception
    assert len(rows) <= 1

    if len(rows) == 0:
        return None

    return rows[0][0].val


def list_form_data_orphans(conn, master_user_id):
    """
    Lists the form data associated with a particular form for a particular
    object where the objects no longer exist
    """

    namespace = 'hms.harvard.edu/omero/forms/data/%'

    params = omero.sys.ParametersI()
    params.add('mid', omero.rtypes.wrap(long(master_user_id)))
    params.add('ns', omero.rtypes.wrap(namespace))

    # Get all the data annotations
    qs = conn.getQueryService()
    q = """
        SELECT anno
        FROM Experimenter user
        JOIN user.annotationLinks links
        JOIN links.child anno
        WHERE anno.class = MapAnnotation
        AND user.id = :mid
        AND anno.ns LIKE :ns
        """

    rows = qs.projection(q, params, conn.SERVICE_OPTS)

    ore = re.compile(
        'hms.harvard.edu/omero/forms/data/'
        '(Project|Dataset|Image|Screen|Plate)([0-9]+)/([A-z0-9]+)'
    )

    obj_types_ids = {}
    obj_form_ids = {}
    for row in rows:
        matches = ore.search(row[0].val.ns.val)

        # Collect the object IDs for each object type
        obj_type = obj_types_ids.setdefault(matches.group(1), [])
        obj_type.append(long(matches.group(2)))
        # collected the form for each object
        obj_form = obj_form_ids.setdefault(
            (matches.group(1), long(matches.group(2))), []
        )
        obj_form.append(matches.group(3))

    for obj_type, obj_ids in obj_types_ids.iteritems():

        params = omero.sys.ParametersI()
        params.add('oids', omero.rtypes.wrap(obj_ids))

        q = """
            SELECT obj.id
            FROM %s obj
            WHERE obj.id IN (:oids)
            """ % obj_type

        conn.SERVICE_OPTS.setOmeroGroup(-1)
        rows = qs.projection(q, params, conn.SERVICE_OPTS)

        for row in rows:
            # Remove the objects which do exist
            obj_form_ids.pop((obj_type, row[0].val))

    for obj, form_ids in obj_form_ids.iteritems():
        for form_id in form_ids:
            yield {
                'form_id': form_id,
                'obj_type': obj[0],
                'obj_id': obj[1]
            }
    return



def add_form_data(conn, master_user_id, form_id, obj_type, obj_id, data,
                  changed_by, changed_at):
    """
    Add form data and associated metadata to the form master user
    """

    # TODO Check and assert that the object exists
    # qs = conn.getQueryService()

    namespace = 'hms.harvard.edu/omero/forms/data/%s%s/%s' % (
        obj_type,
        obj_id,
        form_id
    )

    json_data = _make_form_data_json(form_id, obj_type, obj_id, data,
                                     changed_by, changed_at)

    # If the appropriate annotation already exists, update it
    anno = _get_form_data(conn, master_user_id, form_id, obj_type, obj_id)
    if anno is not None:

        kvs = anno.getMapValue()

        kvs.insert(0, omero.model.NamedValue(
            changed_at.isoformat(), json_data
        ))

        us = conn.getUpdateService()
        us.saveObject(anno, conn.SERVICE_OPTS)

    # If it does not already exist, create a new one
    else:

        mapAnn = omero.gateway.MapAnnotationWrapper(conn)
        mapAnn.setNs(namespace)
        mapAnn.setValue([[changed_at.isoformat(), json_data]])
        mapAnn.save()

        link = omero.model.ExperimenterAnnotationLinkI()
        link.parent = omero.model.ExperimenterI(master_user_id, False)
        link.child = mapAnn._obj

        update = conn.getUpdateService()
        update.saveObject(link, conn.SERVICE_OPTS)


def get_form_data_history(conn, master_user_id, form_id, obj_type, obj_id):
    """
    Get the form data (including history) for the specified form on the
    specified object
    """

    anno = _get_form_data(conn, master_user_id, form_id, obj_type, obj_id)

    if anno is not None:
        kvs = anno.getMapValue()
        for kv in kvs:
            yield _unmake_form_data_json(kv.value)
    else:
        return


def get_form_data(conn, master_user_id, form_id, obj_type, obj_id):
    """
    Get the most recent form data for the specified form on the
    specified object
    """

    return next(
        get_form_data_history(conn, master_user_id, form_id, obj_type, obj_id),
        None
    )


def delete_form_data(conn, master_user_id, form_id, obj_type, obj_id):
    """
    Delete the form data (including history) for the specified form on the
    specified object
    """

    anno = _get_form_data(conn, master_user_id, form_id, obj_type, obj_id)

    if anno is None:
        # TODO Throw exception or something to indicate nothing to delete?
        return

    handle = conn.deleteObjects('MapAnnotation', [anno.id.val])
    cb = omero.callbacks.CmdCallbackI(conn.c, handle)

    while not cb.block(500):
        pass
    err = isinstance(cb.getResponse(), omero.cmd.ERR)
    if err:
        # TODO Throw exception
        pass
        # print cb.getResponse()
    cb.close(True)


def _get_object(conn, obj_type, obj_id):
    """
    Get an object of the specified type and id

    Returns a <ObjType>I object or None
    """

    params = omero.sys.ParametersI()
    params.add('oid', omero.rtypes.wrap(long(obj_id)))

    qs = conn.getQueryService()
    q = """
        SELECT obj
        FROM %s obj
        WHERE obj.id = :oid
        """ % obj_type

    rows = qs.projection(q, params, conn.SERVICE_OPTS)

    # TODO Throw Exception
    assert len(rows) <= 1

    if len(rows) == 0:
        return None

    return rows[0][0].val


def _get_form_kvdata(conn, form_id, obj_type, obj_id):
    """
    Get the form data associated with a particular form for a particular
    object.

    Returns a MapAnnotationI object or None
    """

    namespace = 'hms.harvard.edu/omero/forms/kvdata/%s' % form_id

    params = omero.sys.ParametersI()
    params.add('oid', omero.rtypes.wrap(long(obj_id)))
    params.add('ns', omero.rtypes.wrap(namespace))

    qs = conn.getQueryService()
    q = """
        SELECT anno
        FROM %s obj
        JOIN obj.annotationLinks links
        JOIN links.child anno
        WHERE anno.class = MapAnnotation
        AND obj.id = :oid
        AND anno.ns = :ns
        """ % obj_type

    rows = qs.projection(q, params, conn.SERVICE_OPTS)

    # TODO Throw Exception
    assert len(rows) <= 1

    if len(rows) == 0:
        return None

    return rows[0][0].val


def _navigate_form_data_tree(key, data):
    print type(data)
    if isinstance(data, dict):
        for k, v in data.iteritems():
            compound_key = key or ''
            if key:
                compound_key = key + '_'
            for y in _navigate_form_data_tree(compound_key + k, v):
                yield y
    elif isinstance(data, list):
        for item in data:
            for y in _navigate_form_data_tree(key, item):
                yield y
    else:
        yield [str(key), str(data)]


def add_form_data_to_obj(conn, form_id, obj_type, obj_id, data):
    """
    Get the key-values from the data and attach this to the object
    for conveniance
    """

    namespace = 'hms.harvard.edu/omero/forms/kvdata/%s' % form_id

    # Extract key values from form data
    kvs = _navigate_form_data_tree(None, json.loads(data))

    # If the appropriate annotation already exists, update it
    anno = _get_form_kvdata(conn, form_id, obj_type, obj_id)
    if anno is not None:

        anno.setMapValue([omero.model.NamedValue(k, v) for k, v in kvs])

        us = conn.getUpdateService()
        us.saveObject(anno, conn.SERVICE_OPTS)

    # If it does not already exist, create a new one
    else:

        mapAnn = omero.gateway.MapAnnotationWrapper(conn)
        mapAnn.setNs(namespace)
        mapAnn.setValue(kvs)
        mapAnn.save()

        if obj_type == 'Project':
            link = omero.model.ProjectAnnotationLinkI()
            link.parent = omero.model.ProjectI(obj_id, False)
        elif obj_type == 'Dataset':
            link = omero.model.DatasetAnnotationLinkI()
            link.parent = omero.model.DatasetI(obj_id, False)
        elif obj_type == 'Screen':
            link = omero.model.ScreenAnnotationLinkI()
            link.parent = omero.model.ScreenI(obj_id, False)
        elif obj_type == 'Plate':
            link = omero.model.PlateAnnotationLinkI()
            link.parent = omero.model.PlateI(obj_id, False)
        link.child = mapAnn._obj

        update = conn.getUpdateService()
        update.saveObject(link, conn.SERVICE_OPTS)


def delete_form_kvdata(conn, form_id, obj_type, obj_id):
    """
    Delete the form key-value data annotation for the specified object type
    and id
    """

    anno = _get_form_kvdata(conn, form_id, obj_type, obj_id)

    if anno is None:
        # TODO Throw exception or something to indicate nothing to delete?
        return

    handle = conn.deleteObjects('MapAnnotation', [anno.id.val])
    cb = omero.callbacks.CmdCallbackI(conn.c, handle)

    while not cb.block(500):
        pass
    err = isinstance(cb.getResponse(), omero.cmd.ERR)
    if err:
        # TODO Throw exception
        pass
        # print cb.getResponse()
    cb.close(True)
