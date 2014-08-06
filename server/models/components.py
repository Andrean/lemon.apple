__author__ = 'Andrean'

import datetime
import defs.cmd
import uuid
import hashlib
from bson.objectid import ObjectId
from bson.binary import Binary
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
#   describe ModelSchemas
#
#   System fields:
#   _lemon_field:  if True shows up that dict field is system definition of field
#   type:   Class reference. Shows type of that field
#   ref:    Reference to another Model
#   unique: Ensures index in MongoDB with UNIQUE: TRUE
#   index:  if True Ensures index in MongoDB on that field in PyMongo.ASCENDING order
#
#######################################################################
class AgentSchema(BaseSchema):

    @classmethod
    def setup_schema(cls):
        cls._schema = {
            'agent_id': uuid.UUID,
            'name': str,
            'tags': [str],
            'entities': [ {'type': ObjectId,'ref': Entity, '_lemon_field': True} ],
            '_sysinfo': {
                'network_address': str,
                'last_connect': datetime.datetime,
                'added_at': datetime.datetime
            }
        }


class EntitySchema(BaseSchema):

    @classmethod
    def setup_schema(cls):
        cls._schema = {
            'entity_id': uuid.UUID,
            'agent': {'type': ObjectId, 'ref': Agent, '_lemon_field': True},
            'info': {
                'name': { '_lemon_field':True, 'type': str, 'unique': True},
                'description': str,
                '_added_at': datetime.datetime,
                '_last_check': datetime.datetime,
                'status': str
            },
            'data_items': [ {'type': ObjectId, 'ref': DataItem, '_lemon_field': True} ]
        }


class DataItemSchema(BaseSchema):

    @classmethod
    def setup_schema(cls):
        cls._schema = {
            'name': str,
            'entity': {'type': ObjectId, 'ref': Entity, '_lemon_field': True},
            'data_type': str,
            'contractor': {'type': ObjectId, 'ref': Contractor, '_lemon_field': True},
            'trigger': {'type': ObjectId, 'ref': Trigger, '_lemon_field': True},
            'data': {'type': ObjectId, 'ref': DataMeta, '_lemon_field': True}
        }


class DataMetaSchema(BaseSchema):

    @classmethod
    def setup_schema(cls):
        cls._schema = {
            'meta_id': str,
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
            'meta_id': str,
            'num': int,
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
            'name': { '_lemon_field':True, 'type': str, 'unique': True},
            'data': Binary, # binary object
            '_type': str,
            '_hash': str
        }


class TriggerSchema(BaseSchema):

    @classmethod
    def setup_schema(cls):
        cls._schema = {
            'name': { '_lemon_field':True, 'type': str, 'unique': True},
            'trigger': str
        }
#######################################################################


#######################################################################
# describe models
#
#######################################################################
#######################################################################
#   Model "Agent"
#######################################################################
class Agent(BaseModel):
    """

    """
    Schema = AgentSchema
    Collection = 'agents'
    _index_agentid = None
    _index_tags = None

    def __init__(self, item=None):
        super().__init__(item)
        self.commands = defs.cmd.Commands()

    @classmethod
    def add_new(cls, agent_id, client_host):
        agent = cls()
        agent['agent_id'] = uuid.UUID(agent_id)
        agent['tags'].append(str(agent['agent_id']))
        agent['_sysinfo']['network_address'] = client_host
        agent['_sysinfo']['added_at'] = datetime.datetime.now()
        agent['_sysinfo']['last_connect'] = datetime.datetime.now()
        return agent.save()

    @classmethod
    def add_command(cls, cmd, tags, args=[]):
        command = defs.cmd.Command(cmd, tags, args)
        for agent in cls.findByTag(tags):
            agent.commands.add(command)

    @classmethod
    def create_indexes(cls):
        if cls.Instances is not None:
            pointer = 0
            cls._index_tags = {}
            cls._index_agentid = {}
            for agent in cls.Instances:
                cls._index_agentid[agent['agent_id']] = pointer
                for tag in agent['tags']:
                    if not cls._index_tags.__contains__(tag):
                        cls._index_tags[tag] = []
                    cls._index_tags[tag].append(pointer)

    @classmethod
    def findByAgentId(cls, agent_id):
        if type(agent_id) is not uuid.UUID:
            agent_id = uuid.UUID(agent_id)
        try:
            if cls._index_agentid is not None:
                return cls.Instances[cls._index_agentid[agent_id]]
            conn = cls.get_connection()
            item = conn[cls.Collection].find_one({'agent_id': agent_id})
            if item is not None:
                return cls(item)
        except:
            pass
        return None

    @classmethod
    def findByTag(cls, tags):
        try:
            if cls._index_tags is not None:
                agents = []
                pointers = []
                for tag in tags:
                    index = cls._index_tags.get(tag)
                    if index is not None:
                        for pointer in index:
                            if pointer not in pointers:
                                pointers.append(pointer)
                for pointer in pointers:
                    agents.append(cls.Instances[pointer])
                return agents
            conn = cls.get_connection()
            return [cls(agent) for agent in conn[cls.Collection].find({'tags':{'$in': tags}})]
        except:
            pass
        return []


    @property
    def entities(self):
        return [Entity.findById(e) for e in self['entities']]

    def add_entity(self, entity):
        _id = None
        if isinstance(entity, Entity):
            _id = entity.id
        if type(entity) is ObjectId:
            _id = entity
        if _id is not None and _id not in self['entities']:
            self['entities'].append(_id)
        self.save()

    def del_entity(self, entity):
        if isinstance(entity, Entity):
            _id = entity.id
        if type(entity) is ObjectId:
            _id = entity
        if _id is not None and _id in self['entities']:
            self['entities'].remove(_id)
        self.save()

#######################################################################
#   Model "Entity"
#######################################################################
class Entity(BaseModel):
    Schema = EntitySchema
    Collection = 'entities'
    _index_entity_id = None

    @property
    def agent(self):
        if self['agent'] is not None:
            return Agent.findById(self['agent'])
        return None

    def set_agent(self, agent):
        _id = None
        if isinstance(agent, Agent):
            _id = agent.id
        if type(agent) == ObjectId:
            _id = agent
        last_agent_id = self['agent']
        if last_agent_id is not None:
            agent = Agent.findById(last_agent_id)
            if agent is not None:
                agent.del_entity(self)
        self['agent'] = _id
        agent = Agent.findById(_id)
        if agent is not None:
            agent.add_entity(self)
        self.save()

    @classmethod
    def add_new(cls, agent_id, name, description):
        entity = cls()
        entity['entity_id'] = uuid.uuid4()
        entity['info']['_added_at'] = datetime.datetime.now()
        entity['info']['name'] = str(name)
        entity['info']['description'] = str(description)
        entity['info']['status'] = 'unknown'
        # todo: use trigger to field 'agent' for correct assignment agent
        entity.save() # save to get ObjectId
        entity.set_agent(Agent.findByAgentId(agent_id))
        entity.save()
        return entity

    @classmethod
    def create_indexes(cls):
        if cls.Instances is not None:
            pointer = 0
            cls._index_entity_id = {}
            for e in cls.Instances:
                cls._index_entity_id[e['entity_id']] = pointer

    @classmethod
    def findByEntityId(cls, entity_id):
        if type(entity_id) is not uuid.UUID:
            entity_id = uuid.UUID(entity_id)
        try:
            if cls._index_entity_id is not None:
                return cls.Instances[cls._index_entity_id[entity_id]]
            conn = cls.get_connection()
            item = conn[cls.Collection].find_one({'entity_id': entity_id})
            if item is not None:
                return cls(item)
        except:
            pass
        return None

    def remove(self):
        agent = self.agent
        if agent is not None:
            agent.del_entity(self)
        super().remove()


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

    @classmethod
    def add_new(cls, name, binary_data):
        contractor = cls()
        contractor['name'] = name
        contractor['data'] = Binary(binary_data)
        contractor['_type'] = "python"
        contractor['_hash'] = cls.get_md5(contractor['data'])
        contractor.save()
        return contractor

    @staticmethod
    def get_md5(data):
        md5 = hashlib.md5()
        md5.update(data)
        return md5.hexdigest()

    @property
    def short_view(self):
        data = self._data.copy()
        data['size'] = len(self['data'])
        data['data'] = None
        return data


class Trigger(BaseModel):
    Schema = TriggerSchema
    Collection = 'triggers'
#######################################################################

#######################################################################
# after describe of models we must
# setup schemas
#######################################################################
SetupSchema()
