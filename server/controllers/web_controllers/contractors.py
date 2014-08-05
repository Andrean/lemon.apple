__author__ = 'Andrean'

import core


def get(req, res):
    names = req.query.get('name')
    contractors = []
    manager = core.Instance.Manager
    if names is not None:
        contractors.extend(manager.contractors.list_instances({'name': { '$in': names}}))
    else:
        contractors.extend(manager.contractors.list_instances())
    res.send_json(contractors)

def add(req, res):
    if req.json is not None:
        name = req.json.get('name')
        if name is None:
            raise Exception('Missing "NAME"')
        data = req.json.get('data')
        if data is None:
            raise Exception('Missing "DATA"')
        manager = core.Instance.Manager
        contractor = manager.contractors.add_new(name, data)
        res.send_json({'name': contractor['name']})
        return
    # todo: controllers self error exception need
    res.send_json({'error': 'body is empty'}, 401)

def remove(req, res):
    pass