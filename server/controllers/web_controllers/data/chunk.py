__author__ = 'Andrean'

import core
import defs.errors
import datetime


############################################################################
#   GET data REQUEST
#
#   query params:
#       data_item   : data_items object_id string.
#       from        : datetime string, returns data from that timestamp
#       to          : datetime string, returns data by that timestamp
#       last        : int, returns last <last> data records
#       chunk:      : int, directly access to chunk num <chunk> of <data_item>
#       from_num    : int, request records from <from_num> position
#       end_num     : int, request records to <end_num> position
#
#   returns:
#       [{'data_item': <data_item>, 'data': [ [data, timestamp], [data, timestamp], ... ]}]
#       or
#       {'error': message}
#       or
#       {'error': {'code':int, 'message': str}
############################################################################
def get(req, res):
    data_items = req.query.get('data_item')
    if data_items is None:
        raise defs.errors.LemonAttributeError('"data_item" is empty')
    from_time = req.query.get('from', [None])[0]
    if from_time is not None:
        from_time = datetime.datetime.fromtimestamp(float(from_time))
    to_time = req.query.get('to', [None])[0]
    if to_time is not None:
        to_time = datetime.datetime.fromtimestamp(float(to_time))
    last = req.query.get('last', [None])[0]
    result = []
    manager = core.Instance.Manager
    if last is not None:
        last = int(last)
        for data_item_oid in data_items:
            data_item = manager.data_items.findById(data_item_oid)
            print(datetime.datetime.now())
            chunk = [x for x in data_item.get_last(last)]
            print(datetime.datetime.now())
            result.append(dict(data_item=data_item_oid, data=chunk))
        res.send_json(result)
        return
    for data_item_oid in data_items:
        data_item = manager.data_items.findById(data_item_oid)
        chunk = [x for x in data_item.get_data(_from=from_time, _to=to_time)]
        result.append(dict(data_item=data_item_oid, data=chunk))
    res.send_json(result)


############################################################################
#   HTTP GET data/chunk/count REQUEST
#
#   query params:
#       data_item:  data_items object_id string
#       from     :  datetime string, count from <from> timestamp
#       to       :  datetime string, count to <to> timestamp
#   returns:
#       count of defined data records of <data_item>
#       int
#       or
#       [{'data_item': <data_item>, 'count': count}]
############################################################################
def count(req, res):
    data_items = req.query.get('data_item')
    if data_items is None:
        raise defs.errors.LemonAttributeError('"data_item" is empty')
    from_time = req.query.get('from', [None])[0]
    if from_time is not None:
        from_time = datetime.datetime.fromtimestamp(float(from_time))
    to_time = req.query.get('to', [None])[0]
    if to_time is not None:
        to_time = datetime.datetime.fromtimestamp(float(to_time))
    result = []
    manager = core.Instance.Manager
    for data_item_oid in data_items:
        data_item = manager.data_items.findById(data_item_oid)
        result.append(dict(data_item=data_item_oid, count=data_item.count_data(_from=from_time,_to=to_time)))
    if len(result) == 1:
        res.send_content(result[0]['count'])
    else:
        res.send_json(result)
