__author__ = 'Andrean'

import core

################################################################
#
#
# """
#     Entities management controllers:
#         add_entity: add new entity to database
#         del_entity: remove entity from database
#         get_entities: get list of entities by filter
#             filter:
#                 tags
#         modify_entity: modify one entity
# """
################################################################
entity_manager = {}

"""
    HTTP GET entities REQUEST CONTROLLER
    query params:
    :parameter agent_id
    :parameter entity_id
    :parameter tag
    :parameter populate. What fields must been populated
    :return entities list
"""
def entity_manager__get_entities(req, res):
    agent_ids = req.query.get('agent_id')
    entity_ids = req.query.get('entity_id')
    tags = req.query.get('tag')
    populate = req.query.get('populate',[])
    manager = core.Instance.Manager
    if entity_ids is not None:
        entities = []
        for entity_id in entity_ids:
            entity = manager.entities.get(entity_id)
            if entity is not None:
                entities.append(entity)
        res.send_json([x.populate(*populate).data for x in entities])
        return
    if agent_ids is not None:
        entities = []
        for agent_id in agent_ids:
            agent = manager.agents.get(agent_id)
            if agent is not None:
                entities.extend(agent.entities)
        res.send_json([x.populate(*populate).data for x in entities])
        return
    if tags is not None:
        entities = []
        for agent in manager.agents.values():
            for tag in tags:
                if tag in agent['tags']:
                    entities.extend(agent.entities)
                    break
        res.send_json([x.populate(*populate).data for x in entities])
        return
    res.send_json([x.populate(*populate).data for x in manager.entities.values()])

"""
    HTTP PUT new entity REQUEST CONTROLLER
    query params:
    :parameter name
    :parameter description
    :parameter agent_id
    :return entity_id of new entity
"""
def entity_manager__add_entity(req, res):
    agent_id = req.query.get('agent_id', [None])[0]
    name = req.query.get('name', [None])[0]
    description = req.query.get('description', [None])[0]
    manager = core.Instance.Manager
    result = manager.add_entity(agent_id, name, description)
    if result[0]:
        res.send_json({'entity_id': result[1]})
    else:
        res.send_content(result[1], code=401)

"""
    HTTP POST modify entity REQUEST CONTROLLER
    body params:
    :parameter agent_id
    :parameter name
    :parameter description
    :return HTTP STATUS
"""
def entity_manager__modify_entity(req, res):
    if req.json is not None:
        applied = {} # result is dict of applied items
        manager = core.Instance.Manager
        for modify_args in req.json:
            entity_id = modify_args.get('entity_id')
            entity = manager.entities.get(entity_id)
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
                    agent = manager.get_agent(agent_id)
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
def entity_manager__del_entity(req, res):
    entities = req.query.get('entity_id', [])
    manager = core.Instance.Manager
    for entity_id in entities:
        manager.del_entity(entity_id)
    res.send_content('')

entity_manager['get_entities'] = entity_manager__get_entities
entity_manager['add_entity'] = entity_manager__add_entity
entity_manager['modify_entity'] = entity_manager__modify_entity
entity_manager['del_entity'] = entity_manager__del_entity
################################################################

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
agent_manager = {}


def get_agents(req, res):
    tags = req.query.get('tag')
    populate = req.query.get('populate', [])
    manager = core.Instance.Manager
    agents = []
    if tags is not None:
        for agent in manager.agents.values():
            for tag in tags:
                if tag in agent['tags']:
                    agents.append(agent)
                break
        res.send_json([x.populate(*populate).data for x in agents])
        return
    res.send_json([x.populate(*populate).data for x in manager.agents.values()])

agent_manager['get_agents'] = get_agents
