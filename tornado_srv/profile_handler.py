# -*- coding: utf-8 -*-
import StringIO
from random import choice
import string
import Image

import bson
import datetime
import tornado
from rek.mongo.conn_manager import mongodb_connection_manager
from rek.rekvizitka.models import Company
from rek.tornado_srv.download_handler import DownloadHandler
from rek.tornado_srv.upload_handler import PostUploadStream
from rek.utils import tornado_auth

profile_logos_collection = mongodb_connection_manager.database['company_profile_files.files']
profile_logos_collection.ensure_index([('rek_id', 1), ('rand', 1)])

THUMBNAIL_SIZES = (
    (186, 93, 'logo'),
    (146, 73, 'list_logo'),
    (58, 29, 'post_logo'),
    (48, 24, 'comment_logo'),
    (36, 18, 'repost_logo'))

class ProfileDownloadHandler(DownloadHandler):
    COLLECTION_NAME = 'company_profile_files'

    @tornado.web.asynchronous
    def get(self, *args, **kwargs):
        self.file_type = kwargs.get('filetype')
        self.company_rek = kwargs.get('company_rek')

        if not self.file_type or not self.company_rek:
            raise tornado.web.HTTPError(404)

        ims_value = self.request.headers.get("If-Modified-Since")
        if ims_value is not None:
            self.set_status(304)
            self.finish()
            return

        file = None
        for cur_size_data in THUMBNAIL_SIZES:
            name = cur_size_data[2]
            if self.file_type.startswith(name + '-'):
                number_str = self.file_type[len(name) + 1:self.file_type.find('.')]
                file = self.files_collection.find_one({'rek_id' : self.company_rek,
                                                       'filename' : name,
                                                       'rand' : number_str})
                break
        if self.file_type.startswith('contact_map'):
            file = self.files_collection.find_one({'rek_id' : self.company_rek,
                                                   'filename' : self.file_type.split('.')[0]})

        if not file:
            raise tornado.web.HTTPError(404)

        oid = bson.ObjectId(file['_id'])
        self.file = self.grid_fs.get(oid)

        self.set_header("Content-Type", self.file.content_type)
        self.set_header("Content-Length", self.file.length)

        self.set_header("Expires", datetime.datetime.utcnow() + datetime.timedelta(days=30))
        self.set_header("Cache-Control", "max-age=%d" % (30 * 24 * 3600))
        self.set_header("Last-Modified", datetime.datetime.utcnow() - datetime.timedelta(days=30))

        self.periodic_callback = tornado.ioloop.PeriodicCallback(self.async_callback(self.getFileData), 100,
                                                                 tornado.ioloop.IOLoop.instance())
        self.periodic_callback.start()

@tornado.web.stream_body
class ProfileUploadHandler(PostUploadStream):
    COLLECTION_NAME = 'company_profile_files'
    FILE_TYPES = ['logo', 'contactmap']

    def get_authorized_parameters(self):
        csrf_key = self.get_cookie('csrftoken')
        session_key = self.get_cookie('sessionid')
        user, company, employee = tornado_auth.get_authorized_parameters(csrf_key, session_key, self.request)
        return user, company

    def is_correct_file_type(self, file_type):
        return file_type in self.FILE_TYPES

    def post(self, *args, **kwargs):
        self.request_file_name = self.get_argument('qqfile')
        self.file_type = kwargs.get('filetype')

        if not self.request_file_name or not len(self.request_file_name) or not self.is_correct_file_type(self.file_type):
            self.set_status(400)
            self.finish()
            return

        user, company = self.get_authorized_parameters()
        if not company:
            self.set_status(403)
            self.finish()
            return

        self.company = company

        PostUploadStream.post(self, args, kwargs)

    def after_file_save(self, file_id, filename):
        profile_logos_collection.update({'_id' : file_id},
                                        {'$set' : {'rek_id' : self.company.rek_id}})

        if self.file_type == 'logo':
            self.content_type = 'application/json'
            old_files = profile_logos_collection.find({'rek_id' : self.company.rek_id, 'filename' : self.get_file_name()})

            file_obj = None
            for file in old_files:
                if file['_id'] == file_id:
                    file_obj = file
                    continue
                self.fs.delete(file['_id'])

            logo_file_id, logo_file_rand = self.create_thumbnails(THUMBNAIL_SIZES, file_obj)
            if logo_file_id and logo_file_rand:
                Company.objects.update({'_id' : self.company._id},
                                       {'$set' : {'logo_file_id' : "%s:%s" % (logo_file_id, logo_file_rand)}})
                img_url = "/grid/profile/%s/logo-%s.jpg" % (self.company.rek_id, logo_file_rand)
                self.write('{"success":true, "imgUrl" : "%s"}' % img_url)
            else:
                self.write('{"success":false}')
        elif self.file_type == 'contactmap':
            self.content_type = 'application/json'
            size = self.update_imagefile_sizes(file_id, (558, 338))
            if not size:
                self.write('{"success":false}')
            else:
                url = "/grid/profile/%s/%s.jpg" % (self.company.rek_id, filename)
                self.write('{"success":true, "imgID":"%s", "width":%d, "height":%d, "imgUrl":"%s"}' % (filename, size[0], size[1], url))

    def thumbnail_in_place(self, img, size, filename, file_id):
        converted = img.convert('RGBA')
        converted.thumbnail(size, Image.ANTIALIAS)
        self.fs.delete(file_id)

        new_file = self.fs.new_file(filename = filename, content_type = "image/jpeg")

        out_im = StringIO.StringIO()
        converted.save(out_im, 'JPEG', quality=90)
        out_im.seek(0)
        new_file.write(out_im.getvalue())
        new_file.close()

        profile_logos_collection.update({'_id' : new_file._id},
                                        {'$set' : {'rek_id' : self.company.rek_id,
                                                   'width' : converted.size[0],
                                                   'height' : converted.size[1]}})

        return new_file._id, converted.size

    def update_imagefile_sizes(self, file_id, max_size):
        try:
            im = StringIO.StringIO()
            base_file_obj = self.fs.get(file_id)
            im.write(base_file_obj.read())
            base_file_obj.close()
            im.seek(0)
            img = Image.open(im)

        except Exception:
            self.fs.delete(file_id)
            return None

        size = img.size
        if size[0] > max_size[0] or size[1] > max_size[1]:
            new_file_id, new_size = self.thumbnail_in_place(img, max_size, base_file_obj.filename, file_id)
            if not new_file_id:
                return None
            size = new_size
        else:
            profile_logos_collection.update({'_id' : file_id},
                    {'$set' : {
                    'width' : size[0],
                    'height' : size[1],
                    'contentType' : "image/jpeg"}
                })
        return size

    def rand_hash(self):
        chars = string.digits
        #noinspection PyUnusedLocal
        return ''.join([choice(chars) for i in xrange(8)])

    def get_file_name(self, header =  None):
        if self.file_type == 'logo':
            return 'tmp_logo'
        elif self.file_type == 'contactmap':
            chars = string.letters + string.digits
            #noinspection PyUnusedLocal
            random_hash = ''.join([choice(chars) for i in xrange(10)])
            return 'contact_map%s' % random_hash
        return 'tmp_logo'

    def create_thumbnails(self, sizes, base_file):
        try:
            im = StringIO.StringIO()
            base_file_obj = self.fs.get(base_file['_id'])
            im.write(base_file_obj.read())
            base_file_obj.close()
            im.seek(0)
            img = Image.open(im)
        except Exception:
            self.fs.delete(base_file['_id'])
            return None

        img_width, img_height = img.size

        logo_file_id = None
        logo_file_rand = None
        first_file = True
        rand_hash = self.rand_hash()
        for width, height, file_name in sizes:
            koef = 1.0 * width / height

            img_width_new = int(koef * img_height)
            add_mode = "none"

            if img_width_new > img_width:                       # add left-right whitespace
                gen_size = int(img_width_new), img_height
                add_mode = "left_right"
            elif img_width_new < img_width:                     # add top-bottom whitespace
                gen_size = img_width, int(img_width / koef)
                add_mode = "top_bottom"
            else:                                               # don't add any borders
                gen_size = img_width, img_height

            gen_image = Image.new('RGBA', gen_size, (255, 255, 255, 0))
            converted = img.convert('RGBA')

            if add_mode == "left_right":
                gen_image.paste(converted, (int((gen_image.size[0] - converted.size[0]) / 2.0), 0), mask=converted)
            elif add_mode == "top_bottom":
                gen_image.paste(converted, (0, int((gen_image.size[1] - converted.size[1]) / 2.0)), mask=converted)
            else:
                gen_image = converted

            if gen_image.size[0] < width and gen_image.size[1] < height:
                gen_image = gen_image.resize((width, height), Image.ANTIALIAS)
            else:
                gen_image.thumbnail((width, height), Image.ANTIALIAS)

            old_files = profile_logos_collection.find({'rek_id' : self.company.rek_id, 'filename' : file_name})

            for file in old_files:
                self.fs.delete(file['_id'])

            new_file = self.fs.new_file(filename = file_name, content_type = "image/jpeg")

            out_im = StringIO.StringIO()
            gen_image.save(out_im, 'JPEG', quality=90)
            out_im.seek(0)
            new_file.write(out_im.getvalue())
            new_file.close()

            profile_logos_collection.update({'_id' : new_file._id},
                                            {'$set' : {'rek_id' : self.company.rek_id,
                                                       'rand' : rand_hash}})

            if first_file:
                logo_file_id = new_file._id
                logo_file_rand = rand_hash
                first_file = False

        return logo_file_id, logo_file_rand
