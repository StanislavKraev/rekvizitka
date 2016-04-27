# -*- coding: utf-8 -*-

from gridfs import GridFS
import tornado
from rek.mongo.conn_manager import mongodb_connection_manager
from rek.utils.multipart_form_data_parser import StreamWriteHandler, StreamZeroCopyHandler

@tornado.web.stream_body
class PostUploadStream(StreamWriteHandler):
    CHUNK_LEN = 256 * 1024
    COLLECTION_NAME = ""

    def after_file_save(self, file_id, filename):
        raise Exception("Must be overwritten")

    def post(self, *args, **kwargs):
        content_type = self.request.headers['Content-Type']
        if content_type.split(";")[0] == 'multipart/form-data':
            self.parsed_headers = []
            self.fs = GridFS(mongodb_connection_manager.database, self.COLLECTION_NAME)
            boundary = '--%s' % self.request.headers['Content-Type'].split(";")[1].split("=")[1]
            self.handler = StreamZeroCopyHandler(boundary, '\r\n\r\n', self)
            self.buffer_pos = 0
            self.file = None
            print("content len === " + str(self.request.content_length))

            self.read_chunks()
        elif content_type.lower() == 'application/octet-stream':
            self.fs = GridFS(mongodb_connection_manager.database, self.COLLECTION_NAME)
            self.buffer_pos = 0

            filename = self.get_file_name()
            self.file = self.fs.new_file(filename = filename, content_type = content_type)

            self.read_stream()
        else:
            self.write('Error! Only multipart data!')
            self.finish()

    def read_chunks(self, chunk = ''):
        chunk_len = len(chunk)
        if chunk_len:
            self.set_stream_data(chunk)
            pos = 0
            while pos < chunk_len:
                pos = self.handler.handle(chunk, pos)
            self.handler.flush(pos)
            self.buffer_pos += chunk_len

        chunk_length = min(self.CHUNK_LEN, self.request.content_length - self.buffer_pos)

        if chunk_length > 0:
            self.request.connection.stream.read_bytes(chunk_length, self.read_chunks)
        else:
            self._on_uploaded()

    def read_stream(self, chunk = ''):
        chunk_len = len(chunk)
        if chunk_len:
            self.file.write(chunk)
            self.buffer_pos += chunk_len

        chunk_length = min(self.CHUNK_LEN, self.request.content_length - self.buffer_pos)

        if chunk_length > 0:
            self.request.connection.stream.read_bytes(chunk_length, self.read_stream)
        else:
            self._on_uploaded_stream()

    def _on_uploaded_stream(self):
        if self.file:
            self.file.close()
            self.after_file_save(self.file._id, self.file.filename)
            self.file = None
        self.finish()

    def handle_header(self, header):
        header_data = []
        sub_headers = header.split('\r\n')
        #print('header is here: "%s"' % header)
        for sub in sub_headers:
            if not len(sub):
                continue
            #print('sub header is here: "%s"' % sub)
            parts = sub.split(";")
            first = True
            data = {}
            #print('parts: "%s"' % str(parts))
            for part in parts:
                if not len(part):
                    continue
                #print('part: "%s"' % part)
                if first:
                    name, value = part.split(':')
                    data[name.strip('\r\n \t"\'')] = value.strip('\r\n \t"\'')
                else:
                    name, value = part.split('=')
                    data[name.strip('\r\n \t"\'')] = value.strip('\r\n \t"\'')
                first = False
            header_data.append(data)
        self.parsed_headers.append(header_data)
#        self.write('header: %s' % str(header_data))

    def get_file_name(self, header = None):
        if header:
            return header['filename']
        return 'unknown'

    def handle_file_open(self):
        if self.file:
            raise Exception('File is already open.')
        if not len(self.parsed_headers) or not len(self.parsed_headers):
            raise Exception('Can not open file - no headers received.')
        last_header = self.parsed_headers[-1]
        if len(last_header) < 2 or 'filename' not in last_header[0] or not 'Content-Type' in last_header[1]:
            return
        file_name = self.get_file_name(last_header[0])
        content_type = last_header[1]['Content-Type']
        if not file_name or not len(file_name):
            return
        self.file = self.fs.new_file(filename = file_name, content_type = content_type)
#        self.write('file open: %s (%s)' % (file_name, content_type))

    def handle_file_write(self, data):
        if not self.file:
            return
        self.file.write(data)

    def handle_file_close(self):
        if not self.file:
            return
        self.file.close()
        self.after_file_save(self.file._id, self.file.filename)
        self.file = None

    def _on_uploaded(self):
        self.finish()
