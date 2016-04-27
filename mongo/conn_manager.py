# -*- coding: utf-8 -*-

import sys

from pymongo import Connection
from pymongo.errors import ConnectionFailure
from django.conf import settings
from django.core import signals

class Singleton(type):
    def __init__(cls, name, bases, dict):
        super(Singleton, cls).__init__(name, bases, dict)
        cls.instance = None
    def __call__(cls,*args,**kw):
        if cls.instance is None:
            cls.instance = super(Singleton, cls).__call__(*args, **kw)
        return cls.instance

class ConnectionManager(object):
    __metaclass__ = Singleton
    def __init__(self):
        self._connection = None
        self._db = None

    def _get_connection(self):
        if not self._connection:
            try:
                self._connection = Connection(host=settings.MONGODB_HOST, port=settings.MONGODB_PORT, tz_aware=True)
            except ConnectionFailure, e:
                sys.stderr.write("Could not connect to MongoDB: %s" % e)
                raise e
        return self._connection

    def _get_database(self):
        connection = self.connection
        if not self._db:
            self._db = connection[settings.MONGODB_DB_NAME]
        return self._db
    database = property(_get_database)

    def disconnect(self):
        if self._connection:
            self._connection.close()

    connection = property(_get_connection)

mongodb_connection_manager = ConnectionManager()

#noinspection PyUnusedLocal
def close_connection(**kwargs):
    mongodb_connection_manager.disconnect()

signals.request_finished.connect(close_connection)

