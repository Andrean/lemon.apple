__author__ = 'Andrean'

from modules.base import BaseServerModule
import core
import uuid
import models.components
import defs.cmd


class Manager(BaseServerModule):

    def __init__(self, _core):
        super().__init__(_core, 'Manager')
        self._storage = None
        self._agents = None

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

    def add_agent(self, agent_id):
        self._logger.info("Add new agent {0} to database".format(agent_id))
        agent = models.components.Agent()
        agent['agent_id'] = uuid.UUID(agent_id)
        agent.save()
        self._agents[agent_id] = agent

    def add_command(self, cmd, tags, args=[]):
        command = defs.cmd.Command(cmd, tags, args)
        for agent in self._agents.values():
            for tag in tags:
                if tag in agent['tags']:
                    agent.commands.add(command)
                    break