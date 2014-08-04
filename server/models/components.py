__author__ = 'Andrean'

import datetime
import defs.cmd
import uuid
from bson.objectid import ObjectId
from models.base import BaseModel, BaseSchema
import core


def SetupSchema():
    AgentSchema.setup()
    EntitySchema.setup()
    DataItemSchema.setup()
    DataMetaSchema.setup()
    DataSchema.setup()
    ContractorSchema.setup()
    TriggerSchema.setup()


#######################################################################
# describe schemas
#######################################################################
class AgentSchema(BaseSchema):

    @classmethod
    def setup_schema(cls):
        cls._schema = {
            'agent_id': uuid.UUID,
            'name': "",
            'tags': [""],
            'entities': [ {'type': ObjectId,'ref': Entity} ],
            '_sysinfo': {
                'network_address': "",
                'last_connect': datetime.datetime,
                'added_at': datetime.datetime
            }
        }


class EntitySchema(BaseSchema):

    @classmethod
    def setup_schema(cls):
        cls._schema = {
            'entity_id': uuid.UUID,
            'agent': {'type': ObjectId, 'ref': Agent},
            'info': {
                'name': "",
                'description': "",
                '_added_at': datetime.datetime,
                '_last_check': datetime.datetime,
                'status': ""
            },
            'data_items': [ {'type': ObjectId, 'ref': DataItem} ]
        }


class DataItemSchema(BaseSchema):

    @classmethod
    def setup_schema(cls):
        cls._schema = {
            'name': "",
            'entity': {'type': ObjectId, 'ref': Entity},
            'type': "",
            'contractor': {'type': ObjectId, 'ref':Contractor},
            'trigger': {'type': ObjectId, 'ref': Trigger},
            'data': {'type': ObjectId, 'ref': DataMeta}
        }


class DataMetaSchema(BaseSchema):

    @classmethod
    def setup_schema(cls):
        cls._schema = {
            'meta_id': "",
            'count': 0,
            'last': {
                'data': {},
                'timestamp': datetime.datetime
            }
        }


class DataSchema(BaseSchema):

    @classmethod
    def setup_schema(cls):
        cls._schema = {
            'meta_id': "",
            'num': 0,
            'chunk': [
                {
                    'data': {},
                    'timestamp': datetime.datetime
                }
            ],
            '_firstTimestamp': datetime.datetime,
            '_endTimestamp': datetime.datetime
        }


class ContractorSchema(BaseSchema):

    @classmethod
    def setup_schema(cls):
        cls._schema = {
            'name': "",
            'script': ""
        }


class TriggerSchema(BaseSchema):

    @classmethod
    def setup_schema(cls):
        cls._schema = {
            'name': "",
            'trigger': ""
        }
#######################################################################


#######################################################################
# describe models
#
#######################################################################
class Agent(BaseModel):
    Schema = AgentSchema
    Collection = 'agents'

    def __init__(self, item=None):
        super().__init__(item)
        self.commands = defs.cmd.Commands()

    @property
    def entities(self):
        return self['entities']

    def add_entity(self, entity):
        _id = None
        if isinstance(entity, Entity):
            _id = entity.id
        if type(entity) is ObjectId:
            _id = entity
        if _id is not None and _id not in self.entities:
            self.entities.append(_id)
        self.save()

    def del_entity(self, entity):
        if isinstance(entity, Entity):
            _id = entity.id
        if type(entity) is ObjectId:
            _id = entity
        if _id is not None:
            self.entities.remove(_id)
        self.save()


class Entity(BaseModel):
    Schema = EntitySchema
    Collection = 'entities'

    def set_agent(self, agent):
        _id = None
        if isinstance(agent, Agent):
            _id = agent.id
        if type(agent) == ObjectId:
            _id = agent
        last_agent_id = self['agent']
        if last_agent_id is not None:
            agent = core.Instance.Manager.get_agent(last_agent_id)
            if agent is not None:
                agent.del_entity(self)
        self['agent'] = _id
        agent = core.Instance.Manager.get_agent(_id)
        if agent is not None:
            agent.add_entity(self)
        self.save()


class DataItem(BaseModel):
    Schema = DataItemSchema
    Collection = 'data_items'


class DataMeta(BaseModel):
    Schema = DataMetaSchema
    Collection = 'data_meta'


class Data(BaseModel):
    Schema = DataSchema
    Collection = 'data'


class Contractor(BaseModel):
    Schema = ContractorSchema
    Collection = 'contractors'


class Trigger(BaseModel):
    Schema = TriggerSchema
    Collection = 'triggers'
#######################################################################

#######################################################################
# after describe of models we must
# setup schemas
#######################################################################
SetupSchema()
