 #!/usr/bin/python
# -*- coding: utf-8 -*-
from django.db import models

# Create your models here.

class Region(models.Model):

    id              = models.IntegerField       (max_length=4, unique=True, primary_key=True)
    name            = models.CharField          (max_length=255, unique=True, verbose_name='Название')

    def __unicode__(self):
        return u'%d. %s' % (self.id, self.name)

    class Meta:
        ordering = ['id']
        verbose_name = 'Регион'
        verbose_name_plural = 'Регионы'

class Bank(models.Model):

    id                      = models.IntegerField   (max_length=9, unique=True, primary_key=True)
    name                    = models.CharField      (max_length=255, verbose_name='Название')
    region                  = models.ForeignKey     (Region, blank=True, null=True, verbose_name='Регион')
    city                    = models.CharField      (max_length=255, blank=True, null=True, verbose_name='Город')
    correspondent_account = models.CharField    (max_length=21, blank=True, null=True, verbose_name='Корреспондентский счёт')
    
    def __unicode__(self):
        return u'%d. %s' % (self.id, self.name)

    class Meta:
        ordering = ['region', 'id']
        verbose_name = 'Банк'
        verbose_name_plural = 'Банки'