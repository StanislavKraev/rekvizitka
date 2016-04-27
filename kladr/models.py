#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.db import models
from rek.fields import BigIntegerField, BigForeignKey

class Level(models.Model):

    id              = models.IntegerField       (max_length=4, unique=True, primary_key=True)
    name            = models.CharField          (max_length=255, unique=True, verbose_name='Название')
    description     = models.TextField          (blank=True, verbose_name='Краткое описание')

    def __unicode__(self):
        return u'%d. %s' % (self.id, self.name)

    class Meta:
        ordering = ['id']
        verbose_name = 'Уровень классификации КЛАДР'
        verbose_name_plural = 'CL. Уровни классификации КЛАДР'

class LocationTypesLevel1(models.Model):

    id              = models.IntegerField       (max_length=4, unique=True, primary_key=True)
    name            = models.CharField          (max_length=255, verbose_name='Название')
    abbr            = models.CharField          (max_length=10, verbose_name='Сокращение')

    def __unicode__(self):
        return u'%d. %s' % (self.id, self.name)

    class Meta:
        ordering = ['name']
        verbose_name = 'Тип локаций КЛАДР (уровень 1)'
        verbose_name_plural = 'LT1. Типы локаций КЛАДР (уровень 1)'

class LocationTypesLevel2(models.Model):

    id              = models.IntegerField       (max_length=4, unique=True, primary_key=True)
    name            = models.CharField          (max_length=255, verbose_name='Название')
    abbr            = models.CharField          (max_length=10, verbose_name='Сокращение')

    def __unicode__(self):
        return u'%d. %s' % (self.id, self.name)

    class Meta:
        ordering = ['name']
        verbose_name = 'Тип локаций КЛАДР (уровень 2)'
        verbose_name_plural = 'LT2. Типы локаций КЛАДР (уровень 2)'

class LocationTypesLevel3(models.Model):

    id              = models.IntegerField       (max_length=4, unique=True, primary_key=True)
    name            = models.CharField          (max_length=255, verbose_name='Название')
    abbr            = models.CharField          (max_length=10, verbose_name='Сокращение')

    def __unicode__(self):
        return u'%d. %s' % (self.id, self.name)

    class Meta:
        ordering = ['name']
        verbose_name = 'Тип локаций КЛАДР (уровень 3)'
        verbose_name_plural = 'LT3. Типы локаций КЛАДР (уровень 3)'

class LocationTypesLevel4(models.Model):

    id              = models.IntegerField       (max_length=4, unique=True, primary_key=True)
    name            = models.CharField          (max_length=255, verbose_name='Название')
    abbr            = models.CharField          (max_length=10, verbose_name='Сокращение')

    def __unicode__(self):
        return u'%d. %s' % (self.id, self.name)

    class Meta:
        ordering = ['name']
        verbose_name = 'Тип локаций КЛАДР (уровень 4)'
        verbose_name_plural = 'LT4. Типы локаций КЛАДР (уровень 4)'

class LocationTypesLevel5(models.Model):

    id              = models.IntegerField       (max_length=4, unique=True, primary_key=True)
    name            = models.CharField          (max_length=255, verbose_name='Название')
    abbr            = models.CharField          (max_length=10, verbose_name='Сокращение')

    def __unicode__(self):
        return u'%d. %s' % (self.id, self.name)

    class Meta:
        ordering = ['name']
        verbose_name = 'Тип локаций КЛАДР (уровень 5)'
        verbose_name_plural = 'LT5. Типы локаций КЛАДР (уровень 5)'

class CenterType(models.Model):

    id              = models.IntegerField       (max_length=2, unique=True, primary_key=True)
    description     = models.TextField          (blank=True, verbose_name='Краткое описание')

    def __unicode__(self):
        return u'%d. %s' % (self.id, self.description)

    class Meta:
        ordering = ['id']
        verbose_name = 'Значение флага "центр" для локаций'
        verbose_name_plural = 'CT. Значения флага "центр" для локаций'

class Region(models.Model):

    id              = models.IntegerField       (max_length=2, primary_key=True)
    name            = models.CharField          (max_length=255, verbose_name='Название локации')
    location_type   = models.ForeignKey         ('LocationTypesLevel1', verbose_name='Тип локации')
    postcode        = models.IntegerField       (max_length=6, verbose_name='Почтовый индекс', null=True, blank=True)

    def __unicode__(self):
        return u'%s (#%d)' % (self.name, self.id)

    class Meta:
        ordering = ['name']
        verbose_name = 'Регион'
        verbose_name_plural = 'L1. Регионы'

class District(models.Model):

    id              = models.IntegerField       (max_length=5, primary_key=True)
    region          = models.ForeignKey         ('Region')
    name            = models.CharField          (max_length=255, verbose_name='Название локации')
    location_type   = models.ForeignKey         ('LocationTypesLevel2', verbose_name='Тип локации')
    postcode        = models.IntegerField       (max_length=6, verbose_name='Почтовый индекс', null=True, blank=True)
    center_type     = models.ForeignKey         ('CenterType')

    def __unicode__(self):
        return u'%s (#%d)' % (self.name, self.id)


    class Meta:
        ordering = ['id']
        verbose_name = 'Район региона'
        verbose_name_plural = 'L2. Районы регионов'


class City(models.Model):

    id              = models.IntegerField       (max_length=8, primary_key=True)
    region          = models.ForeignKey         ('Region', null=True, blank=True)
    district        = models.ForeignKey         ('District', null=True, blank=True)
    name            = models.CharField          (max_length=255, verbose_name='Название локации')
    location_type   = models.ForeignKey         ('LocationTypesLevel3', verbose_name='Тип локации')
    postcode        = models.IntegerField       (max_length=6, verbose_name='Почтовый индекс', null=True, blank=True)
    center_type     = models.ForeignKey         ('CenterType')

    def __unicode__(self):
        return u'%s (#%d)' % (self.name, self.id)

    class Meta:
        ordering = ['id']
        verbose_name = 'Город'
        verbose_name_plural = 'L3. Города'

class Town(models.Model):

    id              = BigIntegerField           (max_length=11, primary_key=True)
    city            = models.ForeignKey         ('City', null=True, blank=True)
    region          = models.ForeignKey         ('Region', null=True, blank=True)
    district        = models.ForeignKey         ('District', null=True, blank=True)
    name            = models.CharField          (max_length=255, verbose_name='Название локации')
    location_type   = models.ForeignKey         ('LocationTypesLevel4', verbose_name='Тип локации')
    postcode        = models.IntegerField       (max_length=6, verbose_name='Почтовый индекс', null=True, blank=True)
    center_type     = models.ForeignKey         ('CenterType')

    def __unicode__(self):
        return u'%s (#%d)' % (self.name, self.id)

    class Meta:
        ordering = ['id']
        verbose_name = 'Село или посёлок городского типа'
        verbose_name_plural = 'L4. Сёла, ПГС'

class Street(models.Model):

    id              = BigIntegerField           (max_length=15, primary_key=True)
    town            = BigForeignKey             ('Town', null=True, blank=True)
    city            = models.ForeignKey         ('City', null=True, blank=True)
    region          = models.ForeignKey         ('Region', null=True, blank=True)
    district        = models.ForeignKey         ('District', null=True, blank=True)
    name            = models.CharField          (max_length=255, verbose_name='Название локации')
    location_type   = models.ForeignKey         ('LocationTypesLevel5', verbose_name='Тип локации', null=True, blank=True)
    postcode        = models.IntegerField       (max_length=6, verbose_name='Почтовый индекс', null=True, blank=True)

    def __unicode__(self):
        return u'%s (#%d)' % (self.name, self.id)

    def _name_with_type(self):
        """Returns unified company 'name'. Now it's a shortname or '<Название компании не указано>'"""
        return u'%s %s' % (self.name, self.location_type.abbr)
    name_with_type = property(_name_with_type)

    class Meta:
        ordering = ['id']
        verbose_name = 'Улица'
        verbose_name_plural = 'L5. Улицы'