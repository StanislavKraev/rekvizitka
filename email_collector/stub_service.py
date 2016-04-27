# -*- coding: utf-8 -*-
import re

import time
import signal
import logging
from django.utils import simplejson
import tornado
import tornado.web

from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer
from pymongo import Connection

connection = Connection(host='127.0.0.1', port=27017, tz_aware=True)
mongo_collection = connection['rekvizitka']['stub_email_collection']

def validateEmail(email):
    if len(email) > 7:
        if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) is not None:
            return 1
    return 0


class MainHandler(tornado.web.RequestHandler):
    CONTENT = """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
        "http://www.w3.org/TR/html4/loose.dtd">
<meta http-equiv="X-UA-Compatible" content="IE=7" />
<html>
<head>
    <title>Оставьте свой Email и мы вас пригласим!</title>
</head>
<link rel="stylesheet" type="text/css" href="/media/css/reset.css"/>
<link rel="stylesheet" type="text/css" href="/media/css/email_collector.css"/>
<!--[if lt IE 9]>
<link rel="stylesheet" type="text/css" href="/media/css/base_ie.css"/>
<![endif]-->
<script type="text/javascript" src="/media/js/jquery/jquery-1.7.min.js"></script>
<script type="text/javascript" src="/media/js/jquery/jquery.borderImage.min.js"></script>
<script type="text/javascript" src="/media/js/rek/dialogs.js"></script>
<script type="text/javascript" src="/media/js/rek/email_collector.js"></script>

<body>
<div id="base_container">
    <div id="main_header">
        <span>Деловая сеть REKVIZITKA.RU</span>
    </div>
    <div id="center_block">
        <div class="money"></div>
        <div class="list_block">
            <span class="label">Зачем это мне?</span>
            <ul>
                <li><div class="arrow"></div><div class="text">здесь вы можете встретить своих клиентов, партнеров и конкурентов </div></li>
                <li><div class="arrow"></div><div class="text">здесь вы можете cтать активным участником своей отрасли</div></li>
                <li><div class="arrow"></div><div class="text">здесь вы можете провести переговоры и наладить бизнес</div></li>
                <li><div class="arrow"></div><div class="text">здесь создается электронная экономика и мы начинаем ей сами управлять</div></li>
            </ul>
        </div>
        <div class="text_block">
            <div class="open_date">Скоро запуск.</div>
            <div class="description">Мы обязательно пригласим вас на открытие &mdash;<br/>оставьте, пожалуйста, для этого адрес своей<br/> электронной почты.</div>
        </div>
        <div id="form_block">
            <div class="form_inside_block">
                <div class="form_content">
                    <form action="" method="POST" class="collect_mail">
                        <div class="input_nice ok">
                            <input class="nice" name="email" id="id_email" title="Ваш e-mail" value=""/>
                        </div>
                        <div class="error_message">
                        </div>
                        <div class="button" onclick="$(this).parent().trigger('submit')">&nbsp;</div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>

<!--[if lt IE 9]>

    <script type="text/javascript">
        function AddMailFormUpdate(){
        $('#form_block div.form_inside_block div.form_content form div.input_nice.ok .image1').hide();
        $('#form_block div.form_inside_block div.form_content form div.input_nice.ok .image0').show();
        $('#form_block div.form_inside_block div.form_content form div.input_nice.error .image0').hide();
        $('#form_block div.form_inside_block div.form_content form div.input_nice.error .image1').show();
        }

        $(document).ready(function(){
            rek.utils.preloadImages('/media/img/email_collector/base_container_border.png',
                            '/media/img/email_collector/input_border.png',
                            '/media/img/email_collector/input_border_err.png');

            $('#base_container').borderImage('url("/media/img/email_collector/base_container_border.png") 0 37 37 37');
            $('#form_block div.input_nice').borderImage('url("/media/img/email_collector/input_border.png") 12', '/media/img/email_collector/input_border_err.png');

            setTimeout(function(){
            AddMailFormUpdate();
            }, 1);
        });


    </script>
<![endif]-->
</body>
</html>
"""
    def post(self, *args, **kwargs):
        email = self.get_argument('email', '')
        if len(email):
            add_email = email.lower()
            if validateEmail(add_email):
                email_obj = mongo_collection.find_one({'email' : add_email})
                if not email_obj:
                    email_status = 1
                    mongo_collection.insert({'email' : add_email})
                else:
                    email_status = 2 #Уже такой есть
            else:
                email_status = 3 #неправильный email
        else:
            email_status = 4 #неизвестная ошибка

        data = {'email_status':email_status}
        self.content_type = 'application/json'
        self.write(simplejson.dumps(data))

    def get(self, *args, **kwargs):
        self.write(self.CONTENT)

class Application(tornado.web.Application):
    def __init__(self, transforms):
        handlers = [
            (r"/$", MainHandler),
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
    port = 8083

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
