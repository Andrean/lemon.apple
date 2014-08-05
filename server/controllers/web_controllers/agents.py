__author__ = 'Andrean'

import core

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
    manager = core.Instance.Manager
    if tags is not None:
        res.send_json([agent.populate(*populate) for agent in manager.agents.findByTag(tags)])
        return
    res.send_json([x.populate(*populate) for x in manager.agents.list_instances()])