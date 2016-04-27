# -*- coding: utf-8 -*-
import bson

from rek.mongo.models import ObjectManager

class StaticPage(object):
    objects = None
    
    def __init__(self, name="", alias="", preview="", content="", enabled=False, _id=None):
        self.name = name          # = models.CharField          (max_length=255, unique=True, verbose_name='Название')
        self.alias = alias          #= models.CharField          (max_length=255, unique=True, verbose_name='Alias URL')
        self.preview = preview         #= models.TextField          (blank=True, verbose_name='Краткое описание (превью)')
        self.content = content         #= models.TextField          (verbose_name='Содержимое (полный текст)')
        self.enabled = enabled        #= models.BooleanField       (verbose_name='Включить и отображать страницу')
        self._id = _id

    def save (self):
        if not self._id:
            result = self.objects.collection.insert({
                'name' : self.name,
                'alias' : self.alias,
                'preview' : self.preview,
                'content' : self.content,
                'enabled' : self.enabled
            })

            if isinstance(result, bson.ObjectId):
                self._id = result
                return result
            else:
                raise Exception('Can not add static page')
        self.objects.collection.update({'_id' : self._id}, {
                'name' : self.name,
                'alias' : self.alias,
                'preview' : self.preview,
                'content' : self.content,
                'enabled' : self.enabled
            })
        return self._id

    def delete(self):
        if not self._id:
            return
        self.objects.collection.remove({'_id' : self._id})

StaticPage.objects = ObjectManager(StaticPage, 'static_pages', indexes = [('alias', 1)])