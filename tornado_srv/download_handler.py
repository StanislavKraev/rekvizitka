# -*- coding: utf-8 -*-

from gridfs import GridFS
import tornado
from rek.mongo.conn_manager import mongodb_connection_manager

class DownloadHandler(tornado.web.RequestHandler):
    REQUEST_FILE_BUFFER = 1024 * 256
    COLLECTION_NAME = ""
    def __init__(self, *args, **kwargs):
        super(DownloadHandler, self).__init__( *args, **kwargs)
        self.periodic_callback = None
        self.files_collection = mongodb_connection_manager.database[self.COLLECTION_NAME + '.files']
        self.company_collection = mongodb_connection_manager.database['companies']
        self.grid_fs = GridFS(mongodb_connection_manager.database, self.COLLECTION_NAME)
        self.file = None

    def getFileData(self):
        result = self.file.read(self.REQUEST_FILE_BUFFER)
        if not len(result):
            self.periodic_callback.stop()
            self.finish()
        else:
            self.write(result)
            self.flush()

