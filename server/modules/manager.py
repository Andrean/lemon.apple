__author__ = 'Andrean'

from modules.base import BaseServerModule
import core
import uuid
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