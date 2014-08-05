__author__ = 'Andrean'

import controllers.web_controllers.entitiies as entities
import controllers.web_controllers.agents as agents
import controllers.web_controllers.contractors as contractors

entity_manager = {}
entity_manager['get_entities'] = entities.get
entity_manager['add_entity'] = entities.add
entity_manager['modify_entity'] = entities.modify
entity_manager['del_entity'] = entities.remove

agent_manager = {}
agent_manager['get_agents'] = agents.get_agents

contractors_manager = contractors