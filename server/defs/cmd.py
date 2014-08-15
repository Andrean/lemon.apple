__author__ = 'Andrean'

import enum
from datetime import datetime
from uuid import uuid4
import copy


class BaseCommands(enum.Enum):
    get_info = "_.get_info"


class CommandStatusEnum(enum.IntEnum):
    error = -1
    present = 0
    submit = 1
    pending = 2
    completed = 3


class Command(object):

    def __init__(self, cmd=None, tags=[], args=[]):
        if type(cmd) is dict:
            self.from_dict(cmd)
        if type(cmd) is str:
            self.id = uuid4()
            self.cmd = cmd
            self.tags = tags
            self.args = args
            self.time = datetime.now()
            self.status = CommandStatusEnum.present
            self.response = None

    def from_dict(self, item):
        self.id = copy.deepcopy(item['id'])
        self.cmd = copy.deepcopy(item['cmd'])
        self.tags = copy.deepcopy(item['tags'])
        self.args = copy.deepcopy(item['args'])
        self.time = copy.deepcopy(item['time'])
        self.status = copy.deepcopy(item['status'])
        self.response = copy.deepcopy(item['response'])

    def to_dict(self):
        _dict = {
            'id': self.id,
            'cmd': self.cmd,
            'tags': self.tags,
            'time': self.time,
            'args': self.args,
            'status': self.status,
            'response': self.response
        }
        return _dict


class Commands(object):
    """
        Keeps commands dictionary:
        {
            'command_id': Command
        }
    """
    def __init__(self):
        self.commands = {}

    def __getitem__(self, cmd_id):
        return self.commands.get(cmd_id)

    def __setitem__(self, cmd_id, cmd):
        self.commands[cmd_id] = cmd

    def __delitem__(self, cmd_id):
        self.delete(cmd_id)

    def add(self, command):
        cmd_dict = command.to_dict()
        self_command = Command()
        self_command.from_dict(cmd_dict)
        self.commands[command.id] = self_command

    def find(self, status=None):
        if status is None:
            return [cmd for cmd in self.commands.values()]
        return [cmd for cmd in self.commands.values() if cmd.status == status]

    def dict(self, status=None):
        return [x.to_dict() for x in self.find(status)]

    def delete(self, cmd_id):
        self.commands.pop(cmd_id)