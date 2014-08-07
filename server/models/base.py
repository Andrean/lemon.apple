__author__ = 'Andrean'

import copy
import bson
import bson.objectid
import bson.dbref
import core


class BaseModel(object):
    Schema = None
    Collection = None
    Instances = None
    _index_objectId = None

    def __init__(self, item=None):
        self._dbref = {}
        self._collection = self.__class__.Collection
        self.schema_instance = self.Schema()
        self._raw = self.schema_instance.init_data()
        self._data = self._raw
        self._id = None
        if type(item) is dict:
            self._id = item.get('_id')
            self.load_from(item)
        else:
            self.load(item)

    @classmethod
    def list_instances(cls, filter={}):
        if cls.Instances is not None:
            return cls.Instances
        conn = cls.get_connection()
        return [cls(x) for x in conn[cls.Collection].find(filter)]

    @classmethod
    def findById(cls, obj_id):
        obj_id = bson.objectid.ObjectId(obj_id)
        try:
            if cls._index_objectId is not None:
                return cls.Instances[cls._index_objectId.get(obj_id)]
            else:
                conn = cls.get_connection()
                item = conn[cls.Collection].find_one(obj_id)
                if item is not None:
                    return cls(item)
                return None
        except:
            return None

    @classmethod
    def load_instances(cls):
        conn = cls.get_connection()
        cls.Instances = []
        cls._index_objectId = {}
        pointer = 0
        for item in conn[cls.Collection].find({}):
            model = cls(item)
            cls.Instances.append(model)
            cls._index_objectId[model.id] = pointer
            pointer += 1
        cls.create_indexes()

    @classmethod
    def create_indexes(cls):
        pass

    @staticmethod
    def get_connection():
        return core.Instance.Storage.connection

    def __getitem__(self, item):
        return self._data.get(item)

    def __setitem__(self, key, value):
        if self.schema_instance.is_valid(key, value):
            self._raw[key] = value
            self._data[key] = value
        else:
            raise TypeError("'{0}' is not valid type for key '{1}' in schema".format(value, key))

    def __str__(self):
        return str(self._data)

    @classmethod
    def get_data(cls):
        if cls.Instances is not None:
            return [x.data for x in cls.Instances]
        conn = cls.get_connection()
        return [x for x in conn[cls.Collection].find({})]

    @property
    def data(self):
        return self._data

    @property
    def DbRef(self):
        return self._dbref
    
    @property
    def id(self):
        return self._id

    def load_from(self, item):
        self._raw = item
        self._data = item

    def load(self, _id=None):
        db = self.get_connection()
        if _id is not None:
            self._id = _id
        if self._id is not None:
            self._dbref = bson.dbref.DBRef(self._collection, self._id)
            self._raw = db.dereference(self._dbref)
            self._data = self._raw

    def save(self):
        db = self.get_connection()
        to_save = self._raw
        _id = db[self._collection].save(to_save)
        if type(_id) is bson.ObjectId:
            self._id = _id
            self._dbref = bson.dbref.DBRef(self._collection, self._id)
            self.load_instances()
        return self

    def remove(self):
        db = self.get_connection()
        if self._id is not None:
            db[self._collection].remove({'_id': self._id})
            self.load_instances()

    def populate(self, *fields): # returns populated DATA!!
        data = copy.deepcopy(self._data)
        if len(fields) > 0:
            for k in fields:
                data = self._populate(data, self.schema_instance._schema, k)
        return data
    
    def _populate(self, data, schema, field=None):
        """


        :rtype : returns populated data from parameter "data"
        :param data: data, which need to be populated 
        :param schema: current schema of data
        :param field: field, which need to be populated
        """
        if type(schema) is list:
            if type(data) is not list:
                raise AttributeError
            for i, v in enumerate(data):
                data[i] = self._populate(v, schema[0], field)
            return data
        if type(schema) is not dict:
            return data
        if field is not None:
            v = schema.get(field)
            data[field] = self._populate(data[field], v)
            return data
        _lemon_field = schema.get('_lemon_field')
        if _lemon_field is not True:
            for k, v in schema.items():
                data[k] = self._populate(data[k],v)
            return data
        ref = schema.get('ref')
        if ref is not None:
            model_instance = ref({'_id':data})
            model_instance.load()
            return model_instance.data
        return data

    def find(self, query):
        con = self.get_connection()
        for v in  con[self._collection].find(query):
            yield self.__class__(v)

    @classmethod
    def ensure_index_schema(cls):
        cls.Schema.ensure_index(cls)



class BaseSchema(object):
    _schema = None

    def __init__(self):
        self._instance = None

    @classmethod
    def setup(cls):
        cls.setup_schema()

    @classmethod
    def setup_schema(cls):
        raise NotImplementedError

    def init_data(self):
        schema = copy.deepcopy(self._schema)
        return self._init_data(schema)

    def _init_data(self, schema):
        for k, v in schema.items():
            if type(v) == dict:
                _lemon_field = v.get('_lemon_field')
                if _lemon_field is not None:
                    schema[k] = None
                else:
                    schema[k] = self._init_data(v)
            elif type(v) == list:
                schema[k] = []
            else:
                schema[k] = None
        return schema

    def is_valid(self, key, value):
        item = self._schema.get(key)
        if item is None:
            return False
        if value is None:
            return True
        if type(value) == type(item):
            return True
        if type(value) == item:
            return True
        if type(item) is dict:
            is_lemon_field = item.get('_lemon_field')
            if is_lemon_field is True:
                type_key = item.get('type')
                if isinstance(value, type_key):
                    return True
                return False
        if isinstance(value, item):
            return True
        return False

    @classmethod
    def ensure_index(cls, model):
        assert(issubclass(model, BaseModel))
        connection = model.get_connection()
        collection = model.Collection
        all_indexes = cls._ensure_index(cls._schema)

        def get_index_fields(index):
            if index is None:
                return None, None
            if index is 'unique':
                return True, None
            if index is 'index':
                return None, True
            uniques = []
            indexes = []
            for k, v in index.items():
                result_u, result_i = get_index_fields(v)
                if type(result_u) is list and len(result_u) > 0:
                    for field in result_u:
                        uniques.append(k+'.'+field)
                if result_u is True:
                    uniques.append(k)
                if type(result_i) is list and len(result_i) > 0:
                    for field in result_i:
                        indexes.append(k+'.'+field)
                if result_i is True:
                    indexes.append(k)
            return uniques, indexes

        if type(all_indexes) is dict:
            uniques, indexes = get_index_fields(all_indexes)
            for index in uniques:
                connection[collection].ensure_index(index,unique=True)
            for index in indexes:
                connection[collection].ensure_index(index)

    @classmethod
    def _ensure_index(cls, schema):
        if type(schema) is dict:
            _lemon_field = schema.get('_lemon_field')
            if _lemon_field is True:
                unique = schema.get('unique')
                if unique is True:
                    return 'unique'
                index = schema.get('index')
                if index is True:
                    return 'index'
                return None
            indexes = {}
            for k, v in schema.items():
                indexes[k] = cls._ensure_index(v)
            return indexes
        if type(schema) is list:
            return cls._ensure_index(schema[0])
        return None


class ItemNotFoundException(Exception):
    pass