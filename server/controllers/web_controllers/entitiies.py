__author__ = 'Andrean'

import core

################################################################
#
#
# """
#     Entities management controllers:
#         add: add new entity to database
#         remove: remove entity from database
#         get: get list of entities by filter
#             filter:
#                 tags
#         modify: modify one entity
# """
################################################################
"""
    HTTP GET entities REQUEST CONTROLLER
    query params:
    :parameter agent_id
    :parameter entity_id
    :parameter tag
    :parameter populate. What fields must been populated
    :return entities list
"""
def get(req, res):
    agent_ids = req.query.get('agent_id')
    entity_ids = req.query.get('entity_id')
    tags = req.query.get('tag')
    populate = req.query.get('populate',[])
    manager = core.Instance.Manager
    if entity_ids is not None:
        entities = []
        for entity_id in entity_ids:
            entity = manager.entities.findByEntityId(entity_id)
            if entity is not None:
                entities.append(entity)
        res.send_json([x.populate(*populate) for x in entities])
        return
    if agent_ids is not None:
        entities = []
        for agent_id in agent_ids:
            agent = manager.agents.findByAgentId(agent_id)
            if agent is not None:
                entities.extend(agent.entities)
        res.send_json([x.populate(*populate) for x in entities])
        return
    if tags is not None:
        entities = []
        for agent in manager.agents.findByTag(tags):
            entities.extend(agent.entities)
        res.send_json([x.populate(*populate) for x in entities])
        return
    res.send_json([x.populate(*populate) for x in manager.entities.list_instances()])

"""
    HTTP PUT new entity REQUEST CONTROLLER
    query params:
    :parameter name
    :parameter description
    :parameter agent_id
    :return entity_id of new entity
"""
def add(req, res):
    agent_id = req.query.get('agent_id', [None])[0]
    name = req.query.get('name', [None])[0]
    description = req.query.get('description', [None])[0]
    manager = core.Instance.Manager
    result = manager.entities.add_new(agent_id, name, description)
    if result is not None:
        res.send_json({'entity_id': result['entity_id']})
        return
    res.send_content('', code=401)

"""
    HTTP POST modify entity REQUEST CONTROLLER
    body params:
    :parameter agent_id
    :parameter name
    :parameter description
    :return HTTP STATUS
"""
def modify(req, res):
    if req.json is not None:
        applied = {} # result is dict of applied items
        manager = core.Instance.Manager
        for modify_args in req.json:
            entity_id = modify_args.get('entity_id')
            entity = manager.entities.findByEntityId(entity_id)
            if entity is not None:
                applied[entity_id] = {}
                name = modify_args.get('name')
                description = modify_args.get('description')
                agent_id = modify_args.get('agent_id')
                if name is not None:
                    entity['info']['name'] = name
                    applied[entity_id]['name'] = True
                if description is not None:
                    entity['info']['description'] = description
                    applied[entity_id]['name'] = True
                if agent_id is not None:
                    agent = manager.agents.findByAgentId(agent_id)
                    if agent is not None:
                        entity.set_agent(agent)
                        applied[entity_id]['agent_id'] = True
                entity.save()
        res.send_json(applied)
        return
    res.send_content("request error", code=401)

"""
    HTTP DELETE delete entity REQUEST CONTROLLER
    body params:
    :parameter entity_id
    :return HTTP STATUS
"""
def remove(req, res):
    entities = req.query.get('entity_id', [])
    manager = core.Instance.Manager
    removed = {}
    for entity_id in entities:
        entity = manager.entities.findByEntityId(entity_id)
        removed[entity_id] = None
        if entity is not None:
            entity.remove()
            removed[entity_id] = True
    res.send_json(removed)

################################################################