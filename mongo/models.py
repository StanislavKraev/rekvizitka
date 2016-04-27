import bson
from rek.mongo.conn_manager import mongodb_connection_manager

class ObjectManager(object):
    def __init__(self, object_class, collection_name, indexes = None, unique_indexes = None):
        if not collection_name or not len(collection_name):
            return
        self.object_class = object_class
        capped = getattr(self.object_class, '__capped__', False)
        if collection_name not in mongodb_connection_manager.database.collection_names() and capped:
            self.collection = mongodb_connection_manager.database.create_collection(
                collection_name, capped=True,
                size = object_class.__capped_size__,
                max = object_class.__capped_max__)

        self.collection = mongodb_connection_manager.database[collection_name]
        if indexes and len(indexes):
            for index in indexes:
                index_name, dir = index
                self.collection.ensure_index([(index_name, dir)])

        if unique_indexes and len(unique_indexes):
            for index in unique_indexes:
                index_name, dir = index
                self.collection.ensure_index([(index_name, dir)], unique=True)

    def get_one(self, kwargs):
        data = self.collection.find_one(kwargs)
        if not data:
            return None

        object = self.object_class(data)
        return object

    def get_one_partial(self, kwargs, parts_dict):
        data = self.collection.find_one(kwargs, parts_dict)
        if not data:
            return None
        object = self.object_class(data)
        return object

    def get(self, paramsDict, limit=0, skip=0):
        objects = []
        data_elements = self.collection.find(paramsDict)
        if limit:
            data_elements = data_elements.limit(limit)
        if skip:
            data_elements = data_elements.skip(skip)
        for data in data_elements:
            objects.append(self.object_class(data))
        return objects

    def count(self, params = None):
        if params:
            return self.collection.find(params).count()
        return self.collection.count()

    def update(self, criteria, new_data, safe=False, multi=False):
        return self.collection.update(criteria, new_data, safe=safe, multi=multi)

class SimpleModel(object):
    __capped__ = False
    objects = ObjectManager(None, '')

    def save(self):
        if self._id and self.__capped__:
            raise Exception('Write-once only (capped collection!)')

        data = self._fields()
        if not self._id:
            result = self.objects.collection.insert(data)

            if isinstance(result, bson.ObjectId):
                self._id = result
                return result
            else:
                raise Exception('Can not add element')

        self.objects.collection.update({'_id' : self._id}, data)
        return self._id

    def _fields(self):
        raise Exception('Must be overridden')