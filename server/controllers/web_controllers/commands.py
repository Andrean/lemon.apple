__author__ = 'Andrean'

import core
import defs.errors


def send_to(req, res):
    tags = req.query.get('tag')
    command = req.query.get('command', [None])[0]
    args = req.query.get('arg', [])
    if not isinstance(tags, list):
        raise defs.errors.LemonValueError('tag not found')
    if not isinstance(command, str):
        raise defs.errors.LemonValueError('command must be string')
    if len(tags) > 0:
        manager = core.Instance.Manager
        manager.agents.add_command(command, tags, args)
    res.send_json({})