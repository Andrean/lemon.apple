__author__ = 'Andrean'

import controllers.web_controllers.entitiies as entities
import controllers.web_controllers.agents as agents
import controllers.web_controllers.contractors as contractors
import controllers.web_controllers.data.items as data_items
import controllers.web_controllers.data.chunk
import controllers.web_controllers.commands

entity_manager = {}
entity_manager['get_entities'] = entities.get
entity_manager['add_entity'] = entities.add
entity_manager['modify_entity'] = entities.modify
entity_manager['del_entity'] = entities.remove

data_items_manager = data_items
data_chunks = controllers.web_controllers.data.chunk

contractors_manager = contractors
commands = controllers.web_controllers.commands