__author__ = 'Andrean'

import copy
import bson
import bson.dbref
import core


class BaseModel(object):
    Schema = None
    Collection = None

    def __init__(self, item=None):
        self._dbref = {}
        self._collection = self.__class__.Collection
        self.schema = self.Schema()
        self._raw = self.schema.init_data()
        self._data = self._raw
        if type(item) is dict:
            self._id = item.get('_id')
            self.load_from(item)
        else:
            self._id = item

    def get_connection(self):
        return core.Instance.Storage.connection

    def __getitem__(self, item):
        return self._data.get(item)

    def __setitem__(self, key, value):
        if self.schema.is_valid(key, value):
            self._raw[key] = value
            self._data[key] = value
        else:
            raise TypeError("'{0}' is not valid type for key '{1}' in schema".format(value, key))

    def __str__(self):
        return str(self._data)

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

    def load(self):
        db = self.get_connection()
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

    def populate(self, *fields):
        if len(fields) > 0:
            for k in fields:
                self._data = self._populate(self._data, self.schema, k)
        self._data = self._populate(self._data, self.schema)
    
    def _populate(self, data, schema, field=None):
        """


        :rtype : returns populated data from parameter "data"
        :param data: data, which need to be populated 
        :param schema: current schema of data
        :param field: field, which need to be populated
        """
        if schema is list:
            if data is not list:
                raise AttributeError
            for i, v in enumerate(data):
                data[i] = self._populate(v, schema[0], field)
            return data
        if schema is not dict:
            return data
        if field is not None:
            v = schema.get(field)
            data[field] = self._populate(data[field], v)
            return data
        ref = schema.get('ref')
        if ref is None:
            for k, v in schema.items():
                data[k] = self._populate(data[k],v)
            return data
        model_instance = ref(data)
        data = model_instance.load()
        return data

    def find(self, query):
        con = self.get_connection()
        for v in  con[self._collection].find(query):
            yield self.__class__(v)


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
                _type = v.get('type')
                _ref = v.get('ref')
                if _ref is not None or _type is not None:
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
        if type(value) == type(item):
            return True
        if isinstance(value, item):
            return True
        return False


class ItemNotFoundException(Exception):
    pass