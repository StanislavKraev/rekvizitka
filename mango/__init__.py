import pymongo.errors
from rek.mongo.conn_manager import mongodb_connection_manager

OperationFailure = pymongo.errors.OperationFailure
database = mongodb_connection_manager.database

class Model(object):

    collection = None

    def __init__(self, result):
        self._fields = result

    def __getattr__(self, attr):
        try:
            return self._fields[attr]
        except KeyError:
            return None

    def __setattr__(self, attr, value):
        if attr in ['id', '_fields']:
            object.__setattr__(self, attr, value)
        else:
            self._fields[attr] = value

    def save(self, safe=False):
        self._fields['_id'] = self.collection.save(self._fields, safe=safe)

    def delete(self):
        self.collection.remove({'_id': self._fields.get('_id', None)})
        self._fields['_id'] = None

    def set(self, fields, safe=False):
        self.collection.update({'_id':self.id}, {'$set': fields}, safe=safe)
        self._fields = self.collection.find_one({'_id':self.id})

    def get_id(self):
        return self._fields.get('_id', None)

    def get_doc(self):
        return self._fields

    id = property(get_id)
    doc = property(get_doc)

    @classmethod
    def get(cls, spec):
        if cls.collection:
            result = cls.collection.find_one(spec)
            if result:
                return cls(result)
        return None