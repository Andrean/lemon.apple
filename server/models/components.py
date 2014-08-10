__author__ = 'Andrean'

import datetime
import defs.cmd
import uuid
import hashlib
from defs.search import binary_search
from bson.objectid import ObjectId
from bson.binary import Binary
from models.base import BaseModel, BaseSchema


def SetupSchema():
    AgentSchema.setup()
    EntitySchema.setup()
    DataItemSchema.setup()
    DataChunkSchema.setup()
    ContractorSchema.setup()
    TriggerSchema.setup()


def Le(**kwargs):
    kwargs['_lemon_field'] = True
    return kwargs


#######################################################################
#   describe ModelSchemas
#
#   System fields:
#   _lemon_field:  if True shows up that dict field is system definition of field
#   type:   Class reference. Shows type of that field
#   ref:    Reference to another Model
#   unique: Ensures index in MongoDB with UNIQUE: TRUE
#   index:  if True Ensures index in MongoDB on that field in PyMongo.ASCENDING order
#   default: default value of field
#
#######################################################################
class AgentSchema(BaseSchema):

    @classmethod
    def setup_schema(cls):
        cls._schema = {
            'agent_id': uuid.UUID,
            'name': str,
            'tags': [str],
            'entities': [Le(type=ObjectId, ref=Entity)],
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
            'agent': Le(type=ObjectId, ref=Agent),
            'info': {
                'name': Le(type=str, unique=True),
                'description': str,
                '_added_at': datetime.datetime,
                '_last_check': datetime.datetime,
                'status': str
            },
            'data_items': [ Le(type=ObjectId, ref=DataItem) ]
        }


class DataItemSchema(BaseSchema):

    @classmethod
    def setup_schema(cls):
        cls._schema = {
            'name': str,
            'entity': Le(type=ObjectId, ref=Entity),
            'data_type': str,
            'contractor': Le(type=ObjectId, ref=Contractor),
            'trigger': Le(type=ObjectId, ref=Trigger),
            'data': [Le(type=ObjectId, ref=DataChunk, index=True)]
        }


# Better decision is storing Data in PostgreSQL DB
# todo: use postgresql for this data schema
class DataChunkSchema(BaseSchema):

    @classmethod
    def setup_schema(cls):
        cls._schema = {
            'data_item': Le(type=ObjectId, ref=DataItem, index=True),
            'num': Le(type=int, default=0),
            'size': Le(type=int, default=0),
            'chunk': [
                {
                    'data': dict,
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
            'name': Le(type=str, unique=True),
            'data': Binary, # binary object
            '_type': str,
            '_hash': Le(type=str, unique=True)
        }


class TriggerSchema(BaseSchema):

    @classmethod
    def setup_schema(cls):
        cls._schema = {
            'name': Le(type=str, unique=True),
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

    def addDataItem(self, item):
        if isinstance(item, DataItem):
            if item.id not in self['data_items']:
                self['data_items'].append(item.id)
                item['entity'] = self.id
                item.save()
                self.save()
                return item
        if type(item) is dict:
            item = DataItem.add_new(item['name'], item['data_type'], self, item['contractor'])
            self.save()
            return item
        return None

    def delDataItem(self, item, full_delete=False):
        _id = None
        if isinstance(item, ObjectId):
            _id = item
        if isinstance(item, DataItem):
            _id = item.id
        if _id is not None:
            if _id in self['data_items']:
                self['data_items'].remove(_id)
                item = DataItem.findById(_id)
                item['entity'] = None
                item.save()
                self.save()
            if full_delete is True:
                item.remove()


class DataItem(BaseModel):
    Schema = DataItemSchema
    Collection = 'data_items'

    MaxChunkSize = 256  # max size of DataChunk document field 'chunk'

    @classmethod
    def add_new(cls, name, data_type, entity, contractor):
        data_item = cls()
        data_item['name'] = name
        data_item['data_type'] = data_type
        if isinstance(contractor, Contractor):
            data_item['contractor'] = contractor.id
        elif isinstance(contractor,ObjectId):
            data_item['contractor'] = contractor
        else:
            raise TypeError("contractor is not Contractor or ObjectId")
        e = None
        if isinstance(entity, BaseModel):
            data_item['entity'] = entity.id
            e = Entity.findById(entity.id)
        if isinstance(entity, ObjectId):
            data_item['entity'] = entity
            e = Entity.findById(entity)
        data_item.save()
        if e is not None:
            e.addDataItem(data_item)
        return data_item

    def remove(self):
        if self['entity'] is not None:
            Entity.findById(self['entity']).delDataItem(self)
        super().remove()

    def verify_hash(self, hash):
        assert(isinstance(self['contractor'], ObjectId))
        conn = self.get_connection()
        value = conn[Contractor.Collection].find_one(self['contractor'], fields=['_hash'])
        assert(value is not None)
        return hash == str(value.get('_hash'))

    def add_data(self, data, timestamp):
        if len(self['data']) == 0:
            data_chunk = DataChunk.add_new(self.id, 0)
            data_chunk['_firstTimestamp'] = timestamp
            self['data'].append(data_chunk.id)
            self.save()
        else:
            data_chunk = DataChunk.findById(self['data'][-1])
        assert(isinstance(data_chunk, DataChunk))
        if data_chunk['size'] >= self.MaxChunkSize:
            num = data_chunk['num']
            data_chunk = DataChunk.add_new(self.id, num + 1)
            data_chunk['_firstTimestamp'] = timestamp
            self['data'].append(data_chunk.id)
            self.save()
        data_chunk.insert(data, timestamp)

    def count_data(self, **kwargs):
        pos = self.__getelements_pos(**kwargs)
        if pos is None:
            return 0
        count = (pos[1][0] - pos[0][0])*256 + pos[1][1] - pos[0][1]
        return count

    def get_data_by_num(self, from_num, to_num):
        if from_num >= to_num:
            return []
        from_index_2 = from_num // self.MaxChunkSize
        from_index_1 = from_num - from_index_2 * self.MaxChunkSize
        to_index_2 = to_num // self.MaxChunkSize
        to_index_1 = to_num - to_index_2 * self.MaxChunkSize
        return self.__get_by_pos([[from_index_2, from_index_1], [to_index_2, to_index_1]])

    def get_last(self, last, chunk_num=None):
        counter = 0
        if chunk_num is not None:
            chunk_num = int(chunk_num)
            if chunk_num >= len(self['data']):
                return []
            data_chunk = DataChunk(self['data'][chunk_num])
            chunk = reversed(data_chunk['chunk'])
            for record in chunk:
                if counter < last:
                    yield [record['data'], record['timestamp']]
                    counter += 1
                else:
                    return
            return
        for item in reversed(self['data']):
            if counter >= last:
                break
            data_chunk = DataChunk(item)
            chunk = reversed(data_chunk['chunk'])
            for record in chunk:
                if counter < last:
                    yield [record['data'], record['timestamp']]
                    counter += 1

    def __get_by_pos(self, pos):
        if pos is None:
            return []
        try:
            chunk = DataChunk(self['data'][pos[0][0]])
            if pos[0][0] == pos[1][0]:
                for i, item in enumerate(chunk['chunk']):
                    if i < pos[0][1] or i > pos[1][1]:
                        continue
                    yield [item['data'], item['timestamp']]
            else:
                for i, item in enumerate(chunk['chunk']):
                    if i < pos[0][1]:
                        continue
                    yield [item['data'], item['timestamp']]
                for i in range(pos[0][0]+1, pos[1][0]-1):
                    chunk = DataChunk(self['data'][i])
                    for item in chunk['chunk']:
                        yield [item['data'], item['timestamp']]
                chunk = DataChunk(self['data'][pos[1][1]])
                for i, item in enumerate(chunk['chunk']):
                    if i > pos[1][1]:
                        break
                    yield [item['data'], item['timestamp']]
        except IndexError:
            return []

    def get_data(self, **kwargs):
        pos = self.__getelements_pos(**kwargs)
        return self.__get_by_pos(pos)

    def __getelements_pos(self, **kwargs):
        if len(self['data']) == 0:
            return None
        from_time = kwargs.get('_from')
        if from_time is None:
            from_time = datetime.datetime.min
        to_time = kwargs.get('_to')
        if to_time is None:
            to_time = datetime.datetime.max
        assert(isinstance(from_time, datetime.datetime))
        assert(isinstance(to_time, datetime.datetime))
        if from_time > to_time:
            return None
        from_oid_pos = binary_search(self['data'], from_time, self.__comparator_chunks, strict=False)
        to_oid_pos = binary_search(self['data'], to_time, self.__comparator_chunks, strict=False)
        # last timestamp in data is less than from or first timestamp is greater than to
        if from_oid_pos == 0.5 or to_oid_pos == -0.5:
            return None
        if from_oid_pos == -0.5:
            from_oid_pos = 0
        if to_oid_pos == 0.5:
            to_oid_pos = len(self['data']) -1
        chunk_from = DataChunk(self['data'][from_oid_pos])
        from_num = binary_search(chunk_from['chunk'], from_time, self.__comparator_data_in_chunk, strict=False)
        if from_num < 0:
            from_num = 0
        chunk_to = DataChunk(self['data'][to_oid_pos])
        to_num = binary_search(chunk_to['chunk'], to_time, self.__comparator_data_in_chunk, strict=False)
        if to_num == 0.5:
            to_num = chunk_to['size'] - 1
        return [[from_oid_pos, from_num], [to_oid_pos, to_num]]

    @staticmethod
    def __comparator_chunks(chunk_oid, timestamp):
        chunk = DataChunk(chunk_oid)
        if chunk['_firstTimestamp'] > timestamp:
            return 1
        if chunk['_endTimestamp'] < timestamp:
            return -1
        return 0

    @staticmethod
    def __comparator_data_in_chunk(el, timestamp):
        if el['timestamp'] > timestamp:
            return 1
        if el['timestamp'] < timestamp:
            return -1
        return 0


class DataChunk(BaseModel):
    Schema = DataChunkSchema
    Collection = 'data'

    def __getitem__(self, item):
        if self._id is None:
            return None
        conn = self.get_connection()
        value = conn[self.Collection].find_one(self._id, fields=[item])
        return value.get(item)

    def __setitem__(self, key, value):
        if self._id is None:
            self._data[key] = value
            return
        conn = self.get_connection()
        conn[self.Collection].update({'_id': self._id}, {'$set': {key: value}})

    @property
    def data(self):
        self.force_load()
        return self._data

    def load(self, _id=None):
        self._id = _id

    def force_load(self, _id=None):
        super().load(_id)

    @classmethod
    def add_new(cls, data_item, num):
        chunk = cls()
        chunk.force_load()
        if isinstance(data_item, DataItem):
            chunk['data_item'] = data_item.id
        elif isinstance(data_item, ObjectId):
            chunk['data_item'] = data_item
        else:
            raise TypeError("{0} is not ObjectId or DataItem".format(type(data_item)))
        chunk['num'] = num
        chunk.save()
        return chunk

    def insert(self, data, timestamp):
        assert(isinstance(timestamp, datetime.datetime))
        conn = self.get_connection()
        conn[self.Collection].update(
            {'_id': self.id},
            {
                '$inc': {'size': 1},
                '$push': {'chunk':{'data': data, 'timestamp': timestamp}},
                '$set': {'_endTimestamp': timestamp}
            }
        )

class Contractor(BaseModel):
    Schema = ContractorSchema
    Collection = 'contractors'
    _index_name = None

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

    @classmethod
    def findByName(cls, name):
        try:
            assert(isinstance(name, str))
            conn = cls.get_connection()
            item = conn[cls.Collection].find_one({'name': name})
            if item is not None:
                return cls(item)
        except:
            pass
        return None


class Trigger(BaseModel):
    Schema = TriggerSchema
    Collection = 'triggers'
#######################################################################

#######################################################################
# after describe of models we must
# setup schemas
#######################################################################
SetupSchema()
