__author__ = 'Andrean'


import core
import defs.request
import defs.errors

@defs.request.prepare_agent_request
def get(req, res):
    pass

@defs.request.prepare_agent_request
def push(req, res):
    if req.json is None:
        raise defs.errors.LemonAttributeError('body is empty')
    manager = core.Instance.Manager
    fail_list = []
    data = req.json
    for item in data:
        print(item)
        data_item_oid = item['data_item']
        hash = item['hash']
        data_item = manager.data_items.findById(data_item_oid)
        if data_item is None or data_item.verify_hash(hash) is not True:
            fail_list.append(data_item_oid)
            continue
        value_list = item['data_list']
        for value in value_list:
            data_item.add_data(value['data'], value['timestamp'])
    res.send_json(fail_list)

