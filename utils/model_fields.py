import os
import Image

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from django.db.models.fields.files import ImageField, ImageFieldFile
from django.core.files.base import ContentFile

def _update_ext(filename, new_ext):
    parts = filename.split('.')
    parts[-1] = new_ext
    return '.'.join(parts)


class ResizedImageFieldFile(ImageFieldFile):

    def save(self, name, content, save=True):
        new_content = StringIO()
        new_content_jpg = StringIO()
        
        content.file.seek(0)

        img = Image.open(content.file)
        img.thumbnail((
            self.field.max_width,
            self.field.max_height
            ), Image.ANTIALIAS)


        formats = {'image/pjpeg' : 'JPEG',
                   'image/gif' : 'GIF',
                   'image/x-png' : 'PNG'}
        try:
            format = formats[content._file.content_type]
        except Exception:
            path, format = os.path.splitext(name)
            format = format.upper()
            if format not in ['JPEG', 'PNG', 'GIF']:
                format = 'JPEG'

        img.convert('RGB').save(new_content, format=format, quality=90)

        new_content = ContentFile(new_content.getvalue())
        new_name = _update_ext(name, format.lower())

        #for pisa
        if self.field.jpeg_dublicate_prefix is not None:

            img.convert('RGB').save(new_content_jpg, 'JPEG', quality=90)
            pisa_name = "%s_%s" % (self.field.jpeg_dublicate_prefix, _update_ext(new_name, 'jpeg'))
            pisa_name = self.field.generate_filename(self.instance, pisa_name)
            pisa_content = ContentFile(new_content_jpg.getvalue())
            self.storage.save(pisa_name, pisa_content)

        #end for pisa

        super(ResizedImageFieldFile, self).save(new_name, new_content, save)

    def south_field_triple(self):
        return 'rek.utils.model_fields.ResizedImageFieldFile', [], {}


class ResizedImageField(ImageField):

    attr_class = ResizedImageFieldFile

    def __init__(self, max_width=100, max_height=100, format='PNG', jpeg_dublicate_prefix=None, *args, **kwargs):
        self.jpeg_dublicate_prefix = jpeg_dublicate_prefix
        self.max_width = max_width
        self.max_height = max_height
        self.format = format
        super(ResizedImageField, self).__init__(*args, **kwargs)

    def south_field_triple(self):
        return 'rek.utils.model_fields.ResizedImageField', [], {}

class ResizedReplaceImageFieldFile(ImageFieldFile):

    def prepare_resized_image(self, content, name):
        new_content = StringIO()
        content.file.seek(0)
        img = Image.open(content.file)
        img.thumbnail((
            self.field.max_width,
            self.field.max_height
            ), Image.ANTIALIAS)
        formats = {'image/pjpeg': 'JPEG',
                   'image/gif': 'GIF',
                   'image/x-png': 'PNG'}
        if self.field.format:
            format = self.field.format
        else:
            try:
                format = formats[content._file.content_type]
            except Exception:
                path, format = os.path.splitext(name)
                format = format.upper()
                if format not in ['JPEG', 'PNG', 'GIF']:
                    format = 'JPEG'
        img.convert('RGB').save(new_content, format=format, quality=90)
        new_content = ContentFile(new_content.getvalue())
        new_name = _update_ext(name, format.lower())
        return new_name, img, new_content

    def save(self, name, content, save=True):
        new_name, img, new_content = self.prepare_resized_image(content, self.field.generate_filename(self.instance, name))
        exists_path = self.storage.path(new_name)
        if os.path.exists(exists_path):
            try:
                os.remove(exists_path)
            except Exception:
                pass
        super(ResizedReplaceImageFieldFile, self).save(new_name, new_content, save)

        new_content_jpg = StringIO()
        if self.field.jpeg_dublicate_prefix is not None:

            img.convert('RGB').save(new_content_jpg, 'JPEG', quality=90)
            pisa_name = "%s_%s" % (self.field.jpeg_dublicate_prefix, _update_ext(new_name, 'jpeg'))
            pisa_name = self.field.generate_filename(self.instance, pisa_name)
            pisa_content = ContentFile(new_content_jpg.getvalue())

            exists_path = self.storage.path(pisa_name)
            if os.path.exists(exists_path):
                try:
                    os.remove(exists_path)
                except Exception:
                    pass
            self.storage.save(pisa_name, pisa_content)

    def south_field_triple(self):
        return 'rek.utils.model_fields.ResizedReplaceImageFieldFile', [], {}


class ResizedReplaceImageField(ImageField):

    attr_class = ResizedReplaceImageFieldFile

    def __init__(self, max_width=100, max_height=100, format=None, jpeg_dublicate_prefix=None, *args, **kwargs):
        self.jpeg_dublicate_prefix = jpeg_dublicate_prefix
        self.max_width = max_width
        self.max_height = max_height
        self.format = format
        super(ResizedReplaceImageField, self).__init__(*args, **kwargs)

    def south_field_triple(self):
        return 'rek.utils.model_fields.ResizedReplaceImageField', [], {}

def get_field_ref(model_instance, field_name):
    for field in model_instance._meta.fields:
        if field.name == field_name:
            return field
    return None

def is_valid_inn(inn):
    if not inn.isdigit():
        return False

    inn_len = len(inn)

    if inn_len == 10:
        return int(inn[9]) == ((2 * int(inn[0]) + 4 * int(inn[1]) + 10 * int(inn[2]) + 3 * int(inn[3]) + 5 * int(inn[4]) + 9 * int(inn[5]) + 4 * int(inn[6]) + 6 * int(inn[7]) + 8 * int(inn[8])) % 11) % 10
    elif inn_len == 12:
        num10 = ((7 * int(inn[0]) + 2 * int(inn[1]) + 4 * int(inn[2]) + 10 * int(inn[3]) + 3 * int(inn[4]) + 5 * int(inn[5]) + 9 * int(inn[6]) + 4 * int(inn[7]) + 6 * int(inn[8]) + 8 * int(inn[9])) % 11) % 10
        num11 = ((3 * int(inn[0]) + 7 * int(inn[1]) + 2 * int(inn[2]) + 4 * int(inn[3]) + 10 * int(inn[4]) + 3 * int(inn[5]) + 5 * int(inn[6]) + 9 * int(inn[7]) + 4 * int(inn[8]) + 6 * int(inn[9]) + 8 * int(inn[10])) % 11) % 10
        return int(inn[11]) == num11 and int(inn[10]) == num10

    return False

def is_valid_kpp(kpp):
    return kpp.isdigit() and len(kpp) == 9
