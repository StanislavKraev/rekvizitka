# -*- coding: utf-8 -*-
from django.utils.translation import ugettext as _

class IncFormEnum(object):
    IF_ANO = 1
    IF_AO = 2
    IF_AKFH = 3
    IF_DUP = 4
    IF_ZAO = 5
    IF_IP = 6
    IF_INL = 7
    IF_KFH = 8
    IF_NP = 9
    IF_OIRO = 10
    IF_OD = 11
    IF_ODO = 12
    IF_OOO = 13
    IF_OUL = 14
    IF_OOS = 15
    IF_OAO = 16
    IF_PIF = 17
    IF_PT = 18
    IF_PK = 19
    IF_PRK = 20
    IF_PRT = 21
    IF_SOIDNT = 22
    IF_TOS = 23
    IF_TNV = 24
    IF_TSG = 25
    IF_UP = 26
    IF_UPNPOU = 27
    IF_UPNPHV = 28
    IF_U = 29
    IF_F = 30
    IF_FPG = 31
    IF_FOND = 32
    IF_HTO = 33
    IF_ULYKO = 34
    IF_ULYNO = 35
    
    ALL = (IF_ANO, IF_AO, IF_AKFH, IF_DUP, IF_ZAO, IF_IP,
           IF_INL, IF_KFH, IF_NP, IF_OIRO, IF_OD, IF_ODO,
           IF_OOO, IF_OUL,IF_OOS, IF_OAO, IF_PIF, IF_PT,
           IF_PK, IF_PRK, IF_PRT, IF_SOIDNT, IF_TOS,
           IF_TNV, IF_TSG, IF_UP, IF_UPNPOU, IF_UPNPHV,
           IF_U, IF_F, IF_FPG, IF_FOND, IF_HTO, IF_ULYKO, IF_ULYNO)

    @classmethod
    def choices(cls):
        return ((cls.IF_ANO, cls.type_to_abbr(cls.IF_ANO)),
                (cls.IF_AO, cls.type_to_abbr(cls.IF_AO)),
                (cls.IF_AKFH, cls.type_to_abbr(cls.IF_AKFH)),
                (cls.IF_DUP, cls.type_to_abbr(cls.IF_DUP)),
                (cls.IF_ZAO, cls.type_to_abbr(cls.IF_ZAO)),
                (cls.IF_IP, cls.type_to_abbr(cls.IF_IP)),
                (cls.IF_INL, cls.type_to_abbr(cls.IF_INL)),
                (cls.IF_KFH, cls.type_to_abbr(cls.IF_KFH)),
                (cls.IF_NP, cls.type_to_abbr(cls.IF_NP)),
                (cls.IF_OIRO, cls.type_to_abbr(cls.IF_OIRO)),
                (cls.IF_OD, cls.type_to_abbr(cls.IF_OD)),
                (cls.IF_ODO, cls.type_to_abbr(cls.IF_ODO)),
                (cls.IF_OOO, cls.type_to_abbr(cls.IF_OOO)),
                (cls.IF_OUL, cls.type_to_abbr(cls.IF_OUL)),
                (cls.IF_OOS, cls.type_to_abbr(cls.IF_OOS)),
                (cls.IF_OAO, cls.type_to_abbr(cls.IF_OAO)),
                (cls.IF_PIF, cls.type_to_abbr(cls.IF_PIF)),
                (cls.IF_PT, cls.type_to_abbr(cls.IF_PT)),
                (cls.IF_PK, cls.type_to_abbr(cls.IF_PK)),
                (cls.IF_PRK, cls.type_to_abbr(cls.IF_PRK)),
                (cls.IF_SOIDNT, cls.type_to_abbr(cls.IF_SOIDNT)),
                (cls.IF_TOS, cls.type_to_abbr(cls.IF_TOS)),
                (cls.IF_TNV, cls.type_to_abbr(cls.IF_TNV)),
                (cls.IF_TSG, cls.type_to_abbr(cls.IF_TSG)),
                (cls.IF_UP, cls.type_to_abbr(cls.IF_UP)),
                (cls.IF_UPNPOU, cls.type_to_abbr(cls.IF_UPNPOU)),
                (cls.IF_UPNPHV, cls.type_to_abbr(cls.IF_UPNPHV)),
                (cls.IF_U, cls.type_to_abbr(cls.IF_U)),
                (cls.IF_F, cls.type_to_abbr(cls.IF_F)),
                (cls.IF_FPG, cls.type_to_abbr(cls.IF_FPG)),
                (cls.IF_FOND, cls.type_to_abbr(cls.IF_FOND)),
                (cls.IF_HTO, cls.type_to_abbr(cls.IF_HTO)),
                (cls.IF_ULYKO, cls.type_to_abbr(cls.IF_ULYKO)),
                (cls.IF_ULYNO, cls.type_to_abbr(cls.IF_ULYNO)),)

    @classmethod
    def type_to_abbr(cls, type):
        if type == cls.IF_ANO:
            return _(u'Автономная некоммерческая организация')
        elif type == cls.IF_AO:
            return u'АО'
        elif type == cls.IF_AKFH:
            return u'Ассоциации крестьянских (фермерских) хозяйств'
        elif type == cls.IF_DUP:
            return u'ДУП'
        elif type == cls.IF_ZAO:
            return u'ЗАО'
        elif type == cls.IF_IP:
            return u'ИП'
        elif type == cls.IF_INL:
            return u'Иное неюридическое лицо'
        elif type == cls.IF_KFH:
            return u'Крестьянское (фермерское) хозяйство'
        elif type == cls.IF_NP:
            return u'Некоммерческое партнерство'
        elif type == cls.IF_OIRO:
            return u'Общественная и религиозная организация'
        elif type == cls.IF_OD:
            return u'Общественное движение'
        elif type == cls.IF_ODO:
            return u'ОДО'
        elif type == cls.IF_OOO:
            return u'ООО'
        elif type == cls.IF_OUL:
            return u'Объединение юридических лиц'
        elif type == cls.IF_OOS:
            return u'Орган общественной самодеятельности'
        elif type == cls.IF_OAO:
            return u'ОАО'
        elif type == cls.IF_PIF:
            return u'Паевой инвестиционный фонд'
        elif type == cls.IF_PT:
            return u'Полное товарищество'
        elif type == cls.IF_PK:
            return u'Потребительский кооператив'
        elif type == cls.IF_PRK:
            return u'Производственный кооператив'
        elif type == cls.IF_PRT:
            return u'Простое товарищество'
        elif type == cls.IF_SOIDNT:
            return u'Садоводческое, огородническое или дачное некоммерческое товарищество'
        elif type == cls.IF_TOS:
            return u'Территориальные общественные самоуправления'
        elif type == cls.IF_TNV:
            return u'Товарищество на вере'
        elif type == cls.IF_TSG:
            return u'ТСЖ'
        elif type == cls.IF_UP:
            return u'УП'
        elif type == cls.IF_UPNPOU:
            return u'УП, основанное на праве оперативного управления'
        elif type == cls.IF_UPNPHV:
            return u'УП, основанное на праве хозяйственного ведения'
        elif type == cls.IF_U:
            return u'Учреждение'
        elif type == cls.IF_F:
            return u'Филиал'
        elif type == cls.IF_FPG:
            return u'Финансово-промышленная группа'
        elif type == cls.IF_FOND:
            return u'Фонд'
        elif type == cls.IF_HTO:
            return u'Хозяйственное товарищество и общество'
        elif type == cls.IF_ULYKO:
            return u'Юридическое лицо, являющееся коммерческой организацией'
        elif type == cls.IF_ULYNO:
            return u'Юридическое лицо, являющееся некоммерческой организацией'
        return u'неизвестный'

    @classmethod
    def type_to_fullopf(cls, type):
        if type == cls.IF_ANO:
            return u'Автономная некоммерческая организация'
        elif type == cls.IF_AO:
            return u'Акционерное общество'
        elif type == cls.IF_AKFH:
            return u'Ассоциации крестьянских (фермерских) хозяйств'
        elif type == cls.IF_DUP:
            return u'Дочернее унитарное предприятие'
        elif type == cls.IF_ZAO:
            return u'Закрытое акционерное общество'
        elif type == cls.IF_IP:
            return u'Индивидуальный предприниматель'
        elif type == cls.IF_INL:
            return u'Иное неюридическое лицо'
        elif type == cls.IF_KFH:
            return u'Крестьянское (фермерское) хозяйство'
        elif type == cls.IF_NP:
            return u'Некоммерческое партнерство'
        elif type == cls.IF_OIRO:
            return u'Общественная и религиозная организация'
        elif type == cls.IF_OD:
            return u'Общественное движение'
        elif type == cls.IF_ODO:
            return u'Общество с дополнительной ответственностью'
        elif type == cls.IF_OOO:
            return u'Общество с ограниченной ответственностью'
        elif type == cls.IF_OUL:
            return u'Объединение юридических лиц'
        elif type == cls.IF_OOS:
            return u'Орган общественной самодеятельности'
        elif type == cls.IF_OAO:
            return u'ОАО'
        elif type == cls.IF_PIF:
            return u'Паевой инвестиционный фонд'
        elif type == cls.IF_PT:
            return u'Полное товарищество'
        elif type == cls.IF_PK:
            return u'Потребительский кооператив'
        elif type == cls.IF_PRK:
            return u'Производственный кооператив'
        elif type == cls.IF_PRT:
            return u'Простое товарищество'
        elif type == cls.IF_SOIDNT:
            return u'Садоводческое, огородническое или дачное некоммерческое товарищество'
        elif type == cls.IF_TOS:
            return u'Территориальные общественные самоуправления'
        elif type == cls.IF_TNV:
            return u'Товарищество на вере'
        elif type == cls.IF_TSG:
            return u'Товарищество собственников жилья'
        elif type == cls.IF_UP:
            return u'Унитарное предприятие'
        elif type == cls.IF_UPNPOU:
            return u'Унитарное предприятие, основанное на праве оперативного управления'
        elif type == cls.IF_UPNPHV:
            return u'Унитарное предприятие, основанное на праве хозяйственного ведения'
        elif type == cls.IF_U:
            return u'Учреждение'
        elif type == cls.IF_F:
            return u'Филиал'
        elif type == cls.IF_FPG:
            return u'Финансово-промышленная группа'
        elif type == cls.IF_FOND:
            return u'Фонд'
        elif type == cls.IF_HTO:
            return u'Хозяйственное товарищество и общество'
        elif type == cls.IF_ULYKO:
            return u'Юридическое лицо, являющееся коммерческой организацией'
        elif type == cls.IF_ULYNO:
            return u'Юридическое лицо, являющееся некоммерческой организацией'
        return u'неизвестный'
  