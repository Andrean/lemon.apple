__author__ = 'Andrean'

import core
import defs.errors


def get(req, res):
    entities_id_list = req.query.get('entity_id')
    names = req.query.get('name')
    manager = core.Instance.Manager
    if entities_id_list is not None:
        entities_id = [x.id for x in manager.entities if x['entity_id'] in entities_id_list]
        items = manager.data_items.list_instances({'entity': {'$in': entities_id}})
        if names is not None:
            items = [x for x in items if x['name'] in names]
        res.send_json([x.data for x in items])
        return
    if names is not None:
        res.send_json([x.data for x in manager.data_items.list_instances({'name': {'$in': names}})])
        return
    res.send_json([x.data for x in manager.data_items.list_instances()])


def set(req, res):
    if req.json is None:
        raise defs.errors.LemonAttributeError('empty body')
    _id = req.json.get('_id')
    manager = core.Instance.Manager
    if _id is not None:
        item = manager.data_items.findById(_id)
    else:
        item = manager.data_items.add_new(**(req.json))
    if item is None:
        raise defs.errors.LemonException("data_item not exists")
    for k, v in req.json.items():
        if k is not '_id':
            item[k] = v
    res.send_json(item.id)


def remove(req, res):
    _ids = req.query.get('id')
    removed = []
    if _ids is not None:
        manager = core.Instance.Manager
        for x in _ids:
            item = manager.data_items.findById(x)
            if item is None:
                removed.append({'id': x, 'status': "not found"})
                break
            item.remove()
            removed.append({'id': x, 'status': "not found"})
    res.send_json(removed)
