__author__ = 'Andrean'

import core
import defs.errors


def get(req, res):
    names = req.query.get('name')
    short = req.query.get('short', ["0"])[0]
    contractors = []
    manager = core.Instance.Manager
    if names is not None:
        contractors.extend(manager.contractors.list_instances({'name': { '$in': names}}))
    else:
        contractors.extend(manager.contractors.list_instances())
    if short == "1":
        res.send_json([x.short_view for x in contractors])
        return
    res.send_json([x.data for x in contractors])


def add(req, res):
    if req.json is not None:
        name = req.json.get('name')
        if name is None:
            raise defs.errors.LemonAttributeError('Missing "NAME"')
        data = req.json.get('data')
        if data is None:
            raise defs.errors.LemonAttributeError('Missing "DATA"')
        manager = core.Instance.Manager
        contractor = manager.contractors.add_new(name, data)
        res.send_json({'name': contractor['name']})
        return
    raise defs.errors.LemonAttributeError('body is not JSON')

def remove(req, res):
    pass