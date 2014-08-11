__author__ = 'Andrean'


def prepare_agent_request(f):
    def wrapper(req, res):
        agent_id = req.headers.get('Lemon-Agent-ID')
        if agent_id is None:
            res.send_content('need Lemon Agent')
            return
        req.agent_id = agent_id
        f(req, res)
    return wrapper