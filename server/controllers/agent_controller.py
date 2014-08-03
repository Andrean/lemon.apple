__author__ = 'Andrean'

import core
from defs.cmd import CommandStatusEnum as CmdStatus

def prepare_agent_request(f):
    def wrapper(req, res):
        agent_id = req.headers.get('Lemon-Agent-ID')
        if agent_id is None:
            res.send_content('need Lemon Agent')
            return
        req.agent_id = agent_id
        f(req, res)
    return wrapper

@prepare_agent_request
def _get_commands(req, res):
    manager = core.Instance.Manager
    agent = manager.agents.get(req.agent_id)
    if agent is None:
        # agent not found. Add them to list
        manager.add_agent(req.agent_id)
    cmd_list = manager.agents[req.agent_id].commands.find(CmdStatus.present)
    cmd_list_dict = []
    for cmd in cmd_list:
        cmd_list_dict.append(cmd.to_dict())
    res.send_json(cmd_list_dict)
    for cmd in cmd_list:
        manager.agents[req.agent_id].commands[cmd.id].status = CmdStatus.submit


@prepare_agent_request
def _post_commands(req, res):
    manager = core.Instance.Manager
    agent = manager.agents.get(req.agent_id)
    if agent is None:
        res.send_json({}, code=404)
        return
    if req.json is not None:
        from_commands = req.json
        for command in from_commands:
            agent.commands[command['id']].response = command['response']
            agent.commands[command['id']].status = command['status']
    res.send_json({})


commands = {
    'get': _get_commands,
    'post':_post_commands
}