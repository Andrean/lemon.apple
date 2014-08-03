__author__ = 'Andrean'

import datetime
import defs.cmd
import uuid
from bson.objectid import ObjectId
from models.base import BaseModel, BaseSchema


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
            'entities': [ {'type': ObjectId,'ref': Entity} ]
        }


class EntitySchema(BaseSchema):

    @classmethod
    def setup_schema(cls):
        cls._schema = {
            'entity_id': "",
            'agent': {'type': ObjectId, 'ref': Agent},
            'info': {
                'name': "",
                'description': "",
                '_addedAt': datetime.datetime
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
        if self['agent_id'] not in self['tags']:
            self['tags'].append(self['agent_id'])


class Entity(BaseModel):
    Schema = EntitySchema
    Collection = 'entities'


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
