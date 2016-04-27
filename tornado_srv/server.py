# -*- coding: utf-8 -*-
import os, sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'rek.settings'

sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), '../..'))

import time
import signal
import logging
import tornado
import tornado.web

from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer

from rek.tornado_srv.profile_handler import ProfileDownloadHandler, ProfileUploadHandler

#from pydev import pydevd
#pydevd.settrace('127.0.0.1', port=33321, stdoutToServer=True, stderrToServer=True, suspend=False)

#class SendMailMessage(tornado.web.RequestHandler):
#    @tornado.web.asynchronous
#    def post(self, *args, **kwargs):
#
#        #is authenticated
#        session_key = self.get_cookie('sessionid')
#        #csrf_key = self.get_cookie('csrftoken')
#        user_exists = is_authenticated(session_key)
#        self.write("User exists %s" % (user_exists,))
#
#        #message processing
#        mail_headers = self.get_argument('headers')
#        recipient = self.get_argument('recipient')
#        message_subject = self.get_argument('message_subject')
#        message_body = self.get_argument('message_body')
#
#
#        #work with files
#        mongo_connection = Connection(host='localhost', port=27017)
#        mongo_dbh = mongo_connection['rekvizitka']
#        fs = GridFS(mongo_dbh)
#        for file in self.request.files:
#            oid = fs.put(self.request.files[file][0]['body'], content_type=self.request.files[file][0]['content_type'], filename=self.request.files[file][0]['filename'])
#            self.write("File %s with oid <a href='http://127.0.0.1/tornading/messages/getfiles/?fileid=%s' target='_blank'>%s</a><br>" % (self.request.files[file][0]['filename'], oid, oid))
#
#        mongo_connection.close()
#        self.write("User exists %s" % (user_exists,))

class Application(tornado.web.Application):
    def __init__(self, transforms):
        handlers = [
            (r"/grid/profile/(?P<company_rek>[abcehkmoprtxABCEHKMOPRTX0-9]+)/(?P<filetype>.+)$", ProfileDownloadHandler),
            (r"/grid/send/profile/(?P<filetype>.+)", ProfileUploadHandler),
		]
        tornado.web.Application.__init__(self, handlers, transforms)

def sig_handler(sig, frame):
    """Catch signal and init callback"""
    #noinspection PyUnusedLocal
    f = frame
    logging.warning('Caught signal: %s', sig)
    IOLoop.instance().add_callback(shutdown)

def shutdown():
    """Stop server and add callback to stop i/o loop"""
    logging.info('Stopping http server')
    logging.info('Will shutdown in 2 seconds ...')
    io_loop = IOLoop.instance()
    io_loop.add_timeout(time.time() + 2, io_loop.stop)

def main():
    global http_server
    port = 8089

    http_server = HTTPServer(Application(transforms=[tornado.web.ChunkedTransferEncoding]))
    http_server.listen(port, '127.0.0.1')

    # Init signals handler
    signal.signal(signal.SIGTERM, sig_handler)
    # This will also catch KeyboardInterrupt exception ^C
    signal.signal(signal.SIGINT, sig_handler)

    # Starting ...
    IOLoop.instance().start()

if __name__ == '__main__':
    main()
