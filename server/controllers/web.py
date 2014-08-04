__author__ = 'Andrean'

import core

#############################################################
"""
    Entities management controllers:
        add_entity: add new entity to database
        del_entity: remove entity from database
        get_entities: get list of entities by filter
            filter:
                tags
        modify_entity: modify one entity
"""
entity_manager = {}


def entity_manager__get_entities(req, res):
    agent_ids = req.query.get('agent_id')
    entity_ids = req.query.get('entity_id')
    tags = req.query.get('tags')
    manager = core.Instance.Manager
    if entity_ids is not None:
        entities = []
        for entity_id in entity_ids:
            entity = manager.entities.get(entity_id)
            if entity is not None:
                entities.append(entity)
        res.send_json(entities)
        return
    if agent_ids is not None:
        entities = []
        for agent_id in agent_ids:
            agent = manager.agents.get(agent_id)
            if agent is not None:
                entities.extend(agent.entities)
        res.send_json(entities)
        return
    if tags is not None:
        entities = []
        for agent in manager.agents.values():
            for tag in tags:
                if tag in agent['tags']:
                    entities.extend(agent.entities)
                    break
        res.send_json(entities)
        return
    res.send_json([x for x in manager.entities.values()])


entity_manager['get_entities'] = entity_manager__get_entities