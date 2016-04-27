max_len = 0

class WriteHandler(object):
    def __init__(self):
        self.buffer = ""

        self.data_chunks = []
        self.data_file_open = False

    def set_data(self, data):
        self.data = data

    def write(self, range):
        if len(self.buffer):
            header_data = self.buffer + self.data[range[0]:range[1]]
            self.handle_header(header_data[1:])
            self.buffer = ""
        else:
            header_data = self.data[range[0]:range[1]]
            self.handle_header(header_data[1:])

    def write_data(self, range):
        if not self.data_file_open:
            self.handle_file_open()
            self.data_file_open = True

        self.handle_file_write(self.data[range[0]:range[1]])

    def close_data(self):
        self.handle_file_close()

    def write_data_raw(self, data):
        self.handle_file_write(data)

    def append_header_buffer(self, range):
        self.buffer += self.data[range[0]:range[1]]

    def append_header_buffer_data(self, data):
        self.buffer += data

    def flush(self):
        if len(self.buffer):
            self.handle_header(self.buffer[1:])
            self.buffer = ""

    def handle_header(self, header):
        print('header: "%s"' % header)

    def handle_file_open(self):
        print('file open')

    #noinspection PyUnusedLocal
    def handle_file_write(self, data):
        global max_len
        max_len += len(data)
        print('"%s" - len(%d)' % (data, max_len))

    def handle_file_close(self):
        print('file close')

class StreamZeroCopyHandler(object):
    HEADER = 1
    SEPARATOR = 2
    DATA = 3
    DATA_SEPARATOR = 4
    FLUSHED_SEP = 5
    FLUSHED_DATA_SEP = 6
    POST_DATA_SEP = 7
    FLUSHED_POST_DATA_SEP = 8

    def __init__(self, separator, data_separator, writer):
        self.sep = separator
        self.sep_start = self.sep[0]
        self.sep_len = len(separator)
        self.sep_index = 0
        self.sep_buffer = ""
        self.data_sep = data_separator
        self.data_sep_start = self.data_sep[0]
        self.data_sep_len = len(data_separator)
        self.initial_header = ""
        self.state = self.FLUSHED_SEP
        self.header_start_pos = 0
        self.writer = writer

    def handle(self, chunk="", pos=0):
        if self.state == self.HEADER:
            return self.process_header(chunk, pos)
        elif self.state == self.SEPARATOR:
            return self.process_sep(chunk, pos)
        elif self.state == self.DATA_SEPARATOR:
            return self.process_data_sep(chunk, pos)
        elif self.state == self.DATA:
            return self.process_data(chunk, pos)
        elif self.state == self.FLUSHED_SEP:
            return self.process_flushed_sep(chunk, pos)
        elif self.state == self.FLUSHED_DATA_SEP:
            return self.process_flushed_data_sep(chunk, pos)
        elif self.state == self.POST_DATA_SEP:
            return self.process_post_data_sep(chunk, pos)
        elif self.state == self.FLUSHED_POST_DATA_SEP:
            return self.process_flushed_post_data_sep(chunk, pos)
        else:
            raise Exception("Incorrect state")

    def flush(self, pos):
        if self.state == self.HEADER:
            self.flush_header(pos)
        elif self.state == self.SEPARATOR:
            self.flush_sep(pos)
        elif self.state == self.DATA:
            self.flush_data(pos)
        elif self.state == self.DATA_SEPARATOR:
            self.flush_data_sep(pos)
        elif self.state == self.FLUSHED_SEP:
            self.flush_flushed_sep(pos)
        elif self.state == self.FLUSHED_DATA_SEP:
            self.flush_flushed_data_sep(pos)
        elif self.state == self.POST_DATA_SEP:
            self.flush_post_data_sep(pos)
        elif self.state == self.FLUSHED_POST_DATA_SEP:
            self.flush_flushed_post_data_sep(pos)

    def process_header(self, data, pos):
        chunk = data[pos]
        if chunk == self.sep_start:
            self.state = self.SEPARATOR
            self.sep_start_index = pos
            self.sep_index = 1
            self.sep_buffer = chunk
            return pos + 1
        if chunk == self.data_sep_start:
            self.state = self.DATA_SEPARATOR
            self.sep_start_index = pos
            self.sep_index = 1
            self.sep_buffer = chunk
            return pos + 1
        return pos + 1

    def flush_header(self, pos):
        if pos == self.header_start_pos:
            self.header_start_pos = 0
            return
        self.writer.append_header_buffer((self.header_start_pos, pos))
        self.header_start_pos = 0

    def flush_sep(self, pos):
        self.writer.append_header_buffer((self.header_start_pos, self.sep_start_index))
        self.state = self.FLUSHED_SEP

    def flush_data_sep(self, pos):
        self.writer.append_header_buffer((self.header_start_pos, self.sep_start_index))
        self.state = self.FLUSHED_DATA_SEP

    def flush_post_data_sep(self, pos):
        self.writer.write_data((self.header_start_pos, self.sep_start_index))
        self.state = self.FLUSHED_POST_DATA_SEP

    def flush_data(self, pos):
        if pos == self.header_start_pos:
            self.header_start_pos = 0
            return
        self.writer.write_data((self.header_start_pos, pos))
        self.header_start_pos = 0

    def process_sep(self, data, pos):
        chunk = data[pos]
        if chunk == self.data_sep_start:
            self.state = self.DATA_SEPARATOR
            self.sep_start_index = pos
            self.sep_index = 1
            self.sep_buffer = chunk
            return pos + 1

        if chunk != self.sep[self.sep_index]:
            self.state = self.HEADER
            self.sep_buffer = ""
            return pos + 1

        self.sep_index += 1
        self.sep_buffer += chunk
        if len(self.sep_buffer) >= self.sep_len:
            self.writer.write((self.header_start_pos, self.sep_start_index))

            self.state = self.HEADER
            self.header_start_pos = pos + 1
            self.sep_buffer = ""
        return pos + 1

    def process_data_sep(self, data, pos):
        chunk = data[pos]
        if chunk != self.data_sep[self.sep_index]:
            self.state = self.HEADER
            self.sep_buffer = ""
            return pos + 1

        self.sep_index += 1
        self.sep_buffer += chunk
        if len(self.sep_buffer) >= self.data_sep_len:
            self.writer.write((self.header_start_pos, self.sep_start_index))

            self.state = self.DATA
            self.header_start_pos = pos + 1
            self.sep_buffer = ""
        return pos + 1

    def process_post_data_sep(self, data, pos):
        chunk = data[pos]
        if chunk != self.sep[self.sep_index]:
            self.state = self.DATA
            self.sep_buffer = ""
            return pos + 1

        self.sep_index += 1
        self.sep_buffer += chunk
        if len(self.sep_buffer) >= self.sep_len:
            self.writer.write_data((self.header_start_pos, self.sep_start_index - 1))
            self.writer.close_data()
            self.state = self.HEADER
            self.header_start_pos = pos + 1
            self.sep_buffer = ""
        return pos + 1

    def process_data(self, data, pos):
        found_pos = data.find(self.sep_start, pos)
        if found_pos >= 0:
            new_pos = found_pos
            self.state = self.POST_DATA_SEP
            self.sep_start_index = found_pos
            self.sep_index = 1
            self.sep_buffer = data[new_pos]
            return new_pos + 1

        return len(data)

    def process_flushed_sep(self, data, pos):
        chunk = data[pos]
        if chunk == self.data_sep_start:
            self.state = self.FLUSHED_DATA_SEP
            self.writer.append_header_buffer_data(self.sep_buffer)
            self.sep_start_index = pos
            self.sep_index = 1
            self.sep_buffer = chunk
            return pos + 1

        if chunk != self.sep[self.sep_index]:
            self.state = self.HEADER
            self.header_start_pos = pos
            self.writer.append_header_buffer_data(self.sep_buffer)
            self.sep_buffer = ""
            return pos + 1

        self.sep_index += 1
        self.sep_buffer += chunk
        if len(self.sep_buffer) >= self.sep_len:
            self.writer.flush()
            self.state = self.HEADER
            self.header_start_pos = pos + 1
            self.sep_buffer = ""
        return pos + 1

    def process_flushed_data_sep(self, data, pos):
        chunk = data[pos]
        if chunk != self.data_sep[self.sep_index]:
            self.state = self.HEADER
            self.header_start_pos = pos
            self.writer.append_header_buffer_data(self.sep_buffer)
            self.sep_buffer = ""
            return pos + 1

        self.sep_index += 1
        self.sep_buffer += chunk
        if len(self.sep_buffer) >= self.data_sep_len:
            self.writer.flush()
            self.state = self.DATA
            self.header_start_pos = pos + 1
            self.sep_buffer = ""
        return pos + 1

    def process_flushed_post_data_sep(self, data, pos):
        chunk = data[pos]
        if chunk != self.sep[self.sep_index]:
            self.state = self.DATA
            self.header_start_pos = pos
            self.writer.write_data_raw(self.sep_buffer)
            self.sep_buffer = ""
            return pos + 1

        self.sep_index += 1
        self.sep_buffer += chunk
        if len(self.sep_buffer) >= self.sep_len:
            self.writer.close_data()
            self.state = self.HEADER
            self.header_start_pos = pos + 1
            self.sep_buffer = ""
        return pos + 1

    def flush_flushed_post_data_sep(self, pos):
        self.header_start_pos = 0

    def flush_flushed_sep(self, pos):
        self.header_start_pos = 0

    def flush_flushed_data_sep(self, pos):
        self.header_start_pos = 0

separator = "------WebKitFormBoundary5sB7FqWJ8qABIEcj"
data_sep = "\n\n"

#data = separator + 'file' + data_sep + 'abcdef' * 1024 * 1024  + separator
with open('/home/skraev/testfile.txt', 'rb') as sss:
    data = sss.read()

with open('/home/skraev/Downloads/slogs.txt', 'rb') as ttt:
    datat = ttt.read()
print('initial data len: %d' % len(datat))

writer = WriteHandler()
handler = StreamZeroCopyHandler(separator, data_sep, writer)

pos = 0

part_len = 256
last_pos = len(data)
while pos < last_pos:
    part = data[pos:pos + part_len]
    writer.set_data(part)
    j = 0
    len_part = len(part)
    while j < len_part:
        j = handler.handle(part, j)

    pos += part_len
    handler.flush(j)
