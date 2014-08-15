__author__ = 'Andrean'

import core
import datetime
from defs.cmd import CommandStatusEnum as CmdStatus
import defs.request


@defs.request.prepare_agent_request
def get(req, res):
    manager = core.Instance.Manager
    agent = manager.agents.findByAgentId(req.agent_id)
    if agent is None:
        # agent not found. Add them to list
        agent = manager.agents.add_new(req.agent_id, req.client_address[0])
    agent['_sysinfo']['last_connect'] = datetime.datetime.now()
    agent.save()
    cmd_list = agent.commands.find(CmdStatus.present)
    cmd_list_dict = []
    for cmd in cmd_list:
        cmd_list_dict.append(cmd.to_dict())
    res.send_json(cmd_list_dict)
    for cmd in cmd_list:
        agent.commands[cmd.id].status = CmdStatus.submit


@defs.request.prepare_agent_request
def send(req, res):
    manager = core.Instance.Manager
    agent = manager.agents.findByAgentId(req.agent_id)
    if agent is None:
        res.send_json({}, code=404)
        return
    if req.json is not None:
        from_commands = req.json
        for command in from_commands:
            if agent.commands[command['id']] is not None:
               agent.commands[command['id']].response = command['response']
               agent.commands[command['id']].status = command['status']
    res.send_json({})
