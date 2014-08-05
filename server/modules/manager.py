__author__ = 'Andrean'

from modules.base import BaseServerModule
import core
import uuid
import bson.objectid
import models.components
import defs.cmd
import datetime


class Manager(BaseServerModule):

    def __init__(self, _core):
        super().__init__(_core, 'Manager')
        self._storage = None
        self._agents = None
        self._entities = None

    def start(self):
        self._storage = core.Instance.Storage

    def stop(self):
        pass

    @property
    def agents(self):
        if self._agents is None:
            conn = self._storage.connection
            self._agents = {}
            for k in conn[models.components.Agent.Collection].find({}):
                agent = models.components.Agent(k)
                self._agents[str(agent['agent_id'])] = agent
        return self._agents

    def get_agent(self, _id=None):
        if type(_id) is bson.objectid.ObjectId:
            for agent in self._agents.values():
                if _id == agent.id:
                    return agent
        if type(_id) == uuid.UUID:
            return self._agents.get(_id)
        return None

    def add_agent(self, agent_id, client_host):
        self._logger.info("Add new agent {0} from {1} to database".format(agent_id, client_host))
        agent = models.components.Agent()
        agent['agent_id'] = uuid.UUID(agent_id)
        agent['tags'].append(str(agent['agent_id']))
        agent['_sysinfo']['network_address'] = client_host
        agent['_sysinfo']['added_at'] = datetime.datetime.now()
        agent['_sysinfo']['last_connect'] = datetime.datetime.now()
        agent.save()
        self._agents[agent_id] = agent
        return self._agents[agent_id]

    def add_entity(self, agent_id, name, description):
        self._logger.info("Add new entity {1} to agent {0} to database".format(agent_id, name))
        entity = models.components.Entity()
        entity['entity_id'] = uuid.uuid4()
        entity['info']['_added_at'] = datetime.datetime.now()
        entity['info']['name'] = str(name)
        entity['info']['description'] = str(description)
        entity['info']['status'] = 'unknown'
        entity['agent'] = None
        if agent_id is not None:
            agent = self.agents.get(agent_id)
            if agent is None:
                return [False, 'Agent "{0}" not exists'.format(agent_id)]
            entity['agent'] = agent.id
            entity.save()
            agent.entities.append(entity.id)
            agent.save()
        else:
            entity.save()
        self._entities[entity['entity_id']] = entity
        return [True, entity['entity_id']]


    def add_command(self, cmd, tags, args=[]):
        command = defs.cmd.Command(cmd, tags, args)
        for agent in self._agents.values():
            for tag in tags:
                if tag in agent['tags']:
                    agent.commands.add(command)
                    break

    @property
    def entities(self):
        if self._entities is None:
            conn = self._storage.connection
            self._entities = {}
            for k in conn[models.components.Entity.Collection].find({}):
                entity = models.components.Entity(k)
                self._entities[str(entity['entity_id'])] = entity
        return self._entities

    def del_entity(self, entity):
        entity_id = entity
        if type(entity) is bson.objectid.ObjectId:
            for k, e in self.entities.values():
                if e.id == entity:
                   entity_id = k
        if type(entity) is uuid.UUID:
            entity_id = str(entity)
        if isinstance(entity, models.components.Entity):
            entity_id = str(entity['entity_id'])
        entity = self.entities.get(entity_id)
        if entity is not None:
            agent = self.get_agent(entity['agent'])
            if agent is not None:
                agent.del_entity(entity)
            entity.remove()
            self.entities.pop(entity_id)