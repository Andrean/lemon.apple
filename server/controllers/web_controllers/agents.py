__author__ = 'Andrean'

import core


def select_properties(obj, properties):
    if properties is None:
        return obj
    if type(obj) is list:
        return [select_properties(x, properties) for x in obj]
    if type(obj) is dict:
        new_obj = {}
        for p in properties:
            if p in obj:
                new_obj[p] = obj[p]
        return new_obj
    return obj


################################################################
#
#
# """
#     Agents management controllers:
#         get_agents: get list of agents by filter
#             filter:
#                 tag
# """
################################################################
def get_agents(req, res):
    tags = req.query.get('tag')
    populate = req.query.get('populate', [])
    properties = req.query.get('property')
    manager = core.Instance.Manager
    if tags is not None:
        agents = manager.agents.findByTag(tags)
    else:
        agents = manager.agents.list_instances()
    res.send_json(select_properties([x.populate(*populate) for x in agents], properties))


def get_agent_commands(req, res):
    tags = req.query.get('tag')
    status = req.query.get('status', [None])[0]
    manager = core.Instance.Manager
    if tags is not None:
        agents = manager.agents.findByTag(tags)
    else:
        agents = manager.agents.list_instances()
    res.send_json([x.commands.dict(status) for x in agents])
