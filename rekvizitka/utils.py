# -*- coding: utf-8 -*-

REK1_CODE = "CE9E"

def getCode(addedid, mod):
    """
    This mathematic validate id function example
    argument id, mod (1345, 10)
    x = 1*4+3*3+4*2+5*1 % 10
    """
    addedid=str(addedid)
    summ=0
    k=len(addedid)
    for i in addedid:
        m=int(i)*k
        summ+=m
        k-=1

    code = summ % mod
    return str(code)

def getIDwithCode(x):
    """
    This mathematic validate id function
    return: id + code(mod 10) + (idcode1)code(mod 10)
    """
    x=str(x)
    code1=getCode(x,10)
    x+=code1
    code2=getCode(x,10)
    x+=code2
    return x

def validateID(testid):
    """
    This mathematic test id and code function
    return: 1 when true
    return: 0 when false
    """
    val=False
    testid=str(testid)
    id=testid[:-2]
    trueid=getIDwithCode(id)

    if str(testid)==str(trueid):
        val=True

    return val

translation_map = {
    '0': 0, '1': 1,  '2': 2,  '3': 3,  '4': 4,  '5': 5,  '6': 6,  '7': 7,  '8': 8,  '9': 9,
    'A': 10, 'B': 11, 'C': 12, 'E': 13, 'H': 14, 'K': 15, 'M': 16, 'P': 17, 'T': 18, 'X': 19
    }
translation_list = [str(c) for c in xrange(10)] + ['A', 'B', 'C', 'E', 'H', 'K','M', 'P', 'T', 'X']
rev_translation_map = dict(zip(translation_map.values(), translation_map.keys()))

foundation = 20

class CRC8(object):
    BLOCK_SIZE=1
    DIGEST_SIZE=1

    INIT=0x00
    SUM_REQ="Sum >= 0"

    TEST_DATA="abc"
    TEST_HASH=0x8b

    TABLE=[
        0x00, 0x07, 0x0e, 0x09, 0x1c, 0x1b, 0x12, 0x15,
        0x38, 0x3f, 0x36, 0x31, 0x24, 0x23, 0x2a, 0x2d,
        0x70, 0x77, 0x7e, 0x79, 0x6c, 0x6b, 0x62, 0x65,
        0x48, 0x4f, 0x46, 0x41, 0x54, 0x53, 0x5a, 0x5d,
        0xe0, 0xe7, 0xee, 0xe9, 0xfc, 0xfb, 0xf2, 0xf5,
        0xd8, 0xdf, 0xd6, 0xd1, 0xc4, 0xc3, 0xca, 0xcd,
        0x90, 0x97, 0x9e, 0x99, 0x8c, 0x8b, 0x82, 0x85,
        0xa8, 0xaf, 0xa6, 0xa1, 0xb4, 0xb3, 0xba, 0xbd,
        0xc7, 0xc0, 0xc9, 0xce, 0xdb, 0xdc, 0xd5, 0xd2,
        0xff, 0xf8, 0xf1, 0xf6, 0xe3, 0xe4, 0xed, 0xea,
        0xb7, 0xb0, 0xb9, 0xbe, 0xab, 0xac, 0xa5, 0xa2,
        0x8f, 0x88, 0x81, 0x86, 0x93, 0x94, 0x9d, 0x9a,
        0x27, 0x20, 0x29, 0x2e, 0x3b, 0x3c, 0x35, 0x32,
        0x1f, 0x18, 0x11, 0x16, 0x03, 0x04, 0x0d, 0x0a,
        0x57, 0x50, 0x59, 0x5e, 0x4b, 0x4c, 0x45, 0x42,
        0x6f, 0x68, 0x61, 0x66, 0x73, 0x74, 0x7d, 0x7a,
        0x89, 0x8e, 0x87, 0x80, 0x95, 0x92, 0x9b, 0x9c,
        0xb1, 0xb6, 0xbf, 0xb8, 0xad, 0xaa, 0xa3, 0xa4,
        0xf9, 0xfe, 0xf7, 0xf0, 0xe5, 0xe2, 0xeb, 0xec,
        0xc1, 0xc6, 0xcf, 0xc8, 0xdd, 0xda, 0xd3, 0xd4,
        0x69, 0x6e, 0x67, 0x60, 0x75, 0x72, 0x7b, 0x7c,
        0x51, 0x56, 0x5f, 0x58, 0x4d, 0x4a, 0x43, 0x44,
        0x19, 0x1e, 0x17, 0x10, 0x05, 0x02, 0x0b, 0x0c,
        0x21, 0x26, 0x2f, 0x28, 0x3d, 0x3a, 0x33, 0x34,
        0x4e, 0x49, 0x40, 0x47, 0x52, 0x55, 0x5c, 0x5b,
        0x76, 0x71, 0x78, 0x7f, 0x6a, 0x6d, 0x64, 0x63,
        0x3e, 0x39, 0x30, 0x37, 0x22, 0x25, 0x2c, 0x2b,
        0x06, 0x01, 0x08, 0x0f, 0x1a, 0x1d, 0x14, 0x13,
        0xae, 0xa9, 0xa0, 0xa7, 0xb2, 0xb5, 0xbc, 0xbb,
        0x96, 0x91, 0x98, 0x9f, 0x8a, 0x8d, 0x84, 0x83,
        0xde, 0xd9, 0xd0, 0xd7, 0xc2, 0xc5, 0xcc, 0xcb,
        0xe6, 0xe1, 0xe8, 0xef, 0xfa, 0xfd, 0xf4, 0xf3
    ]

    def __init__(self, sum=0x00):
        self.sum=sum^0xff

    def sumValid(self, sum):
        return sum>=0

    def update(self, b):
        self.sum=self.TABLE[self.sum^b % 240]

    def digest(self):
        return self.sum^0xff

    def xdigest(self):
        d = self.digest()
        res = 0
        for c in str(d):
            res ^= int(c)
        return translation_list[res]

def charify(val):
    res = ""
    while val > 0:
        res += rev_translation_map[val % foundation]
        val //= foundation
    return res[::-1]

def decharify(code):
    try:
        code = code.upper().replace(u'А', 'A')
        code = code.upper().replace(u'В', 'B')
        code = code.upper().replace(u'С', 'C')
        code = code.upper().replace(u'Е', 'E')
        code = code.upper().replace(u'Н', 'H')
        code = code.upper().replace(u'К', 'K')
        code = code.upper().replace(u'М', 'M')
        code = code.upper().replace(u'Р', 'P')
        code = code.upper().replace(u'Т', 'T')
        code = code.upper().replace(u'Х', 'X')

        position = 0
        result = 0
        for i in code[::-1]:
            result += pow(foundation, position) * translation_map[i]
            position += 1
    except Exception:
        result = 0
    return result


def integer_to_code(val):

    c = CRC8()
    c.update(val)
    di = c.xdigest()
    return charify(val) + str(di)

def code_to_integer(val):
    if not isinstance(val, basestring) or len(val) < 3:
        return 0
    try:
        value = decharify(val[:-1])
        code = val[-1:]
    except ValueError:
        return 0

    c = CRC8()
    c.update(value)
    di = c.xdigest()
    if di != code:
        return 0
    return value

def summ_words(sums, fix='.'):

    
    rub_ed = {
        '1': 'один рубль',
        '2': 'два рубля',
        '3': 'три рубля',
        '4': 'четыре рубля',
        '5': 'пять рублей',
        '6': 'шесть рублей',
        '7': 'семь рублей',
        '8': 'восемь рублей',
        '9': 'девять рублей',
        '0': 'рублей'
        }

    rub_des = {
        '1': 'десять',
        '2': 'двадцать',
        '3': 'тридцать',
        '4': 'сорок',
        '5': 'пятьдесят',
        '6': 'шестьдесят',
        '7': 'семьдесят',
        '8': 'восемьдесят',
        '9': 'девяносто',
        '0': ''
        }

    rub_sot = {
        '1': 'сто',
        '2': 'двести',
        '3': 'триста',
        '4': 'четыреста',
        '5': 'пятьсот',
        '6': 'шестьсот',
        '7': 'семьсот',
        '8': 'восемьсот',
        '9': 'девятьсот',
        '0': ''
        }

    rub_tys = {
        '1': 'одна тысяча',
        '2': 'две тысячи',
        '3': 'три тысячи',
        '4': 'четыре тысячи',
        '5': 'пять тысяч',
        '6': 'шесть тысяч',
        '7': 'семь тысяч',
        '8': 'восемь тысяч',
        '9': 'девять тысяч',
        '0': 'тысяч'
        }

    rub_mil = {
        '1': 'один миллион',
        '2': 'два миллиона',
        '3': 'три миллиона',
        '4': 'четыре миллиона',
        '5': 'пять миллионов',
        '6': 'шесть миллионов',
        '7': 'семь миллионов',
        '8': 'восемь миллионов',
        '9': 'девять миллионов',
        '0': 'миллионов'
        }
    #исключения
    rub_isk = {
        '10': 'десять',
        '11': 'одиннадцать',
        '12': 'двенадцать',
        '13': 'тринадцать',
        '14': 'четырнадцать',
        '15': 'пятнадцать',
        '16': 'шестнадцать',
        '17': 'семнадцать',
        '18': 'восемнадцать',
        '19': 'девятнадцать'
        }

    kop_ed = {
        '1': 'копейка',
        '2': 'копейки',
        '3': 'копейки',
        '4': 'копейки'
        }

    tmp_r = ""
    tmp_k = ""
    lst_sot = []
    lst_mil = []

    #разделяем рубли и копейки по фиксатору, который можно задать самим
    try:
        rub, kop = sums.split(fix)
        rub_lst = list(rub)
        kop_lst = list(kop)

        #разбиваем сумму рублей по 3 цифры
        if len(rub_lst) > 3:
            lst_ed = rub_lst[-3:]
            lst_sot = rub_lst[:-3]
        else:
            lst_ed = rub_lst
        if len(rub_lst) > 6:
            lst_tys = lst_sot[-3:]
            lst_mil = lst_sot[:-3]
        else:
            lst_tys = lst_sot

        #составляем кусок с миллионами
        if lst_mil != []:
            if len(lst_mil) == 1:
                tmp_r = rub_mil.get(lst_mil[0])
            elif len(lst_mil) == 2:
                if lst_mil[0] == '1':
                    tmp_r = rub_isk.get(lst_mil[0]+lst_mil[1])+' миллионов'
                else:
                    tmp_r = rub_des.get(lst_mil[0])+ ' ' +rub_mil.get(lst_mil[1])
            elif len(lst_mil) == 3:
                if lst_mil[1] == '1':
                    tmp_r = rub_sot.get(lst_mil[0])+' '+ \
                            rub_isk.get(lst_mil[1]+lst_mil[2])+' миллионов'
                elif lst_mil[1] == '0' and lst_mil[2] != '0':
                    tmp_r = rub_sot.get(lst_mil[0])+' '+rub_mil.get(lst_mil[2])
                elif lst_mil[1] == '0' and lst_mil[2] == '0':
                    tmp_r = rub_sot.get(lst_mil[0])+' миллионов'
                else:
                    tmp_r = rub_sot.get(lst_mil[0])+' '+ \
                            rub_des.get(lst_mil[1])+' '+rub_mil.get(lst_mil[2])
            tmp_r = tmp_r+' '

        #составляем кусок с тысячами
        if lst_tys != [] and lst_tys != ['0', '0', '0']:
            if len(lst_tys) == 1:
                tmp_r = tmp_r+rub_tys.get(lst_tys[0])
            elif len(lst_tys) == 2:
                if lst_tys[0] == '1':
                    tmp_r = tmp_r+rub_isk.get(lst_tys[0]+lst_tys[1])+' тысяч'
                else:
                    tmp_r = tmp_r+rub_des.get(lst_tys[0])+rub_tys.get(lst_tys[1])
            elif len(lst_tys) == 3:
                if lst_tys[0] != '0':
                    if lst_tys[1] == '1':
                        tmp_r = tmp_r+rub_sot.get(lst_tys[0])+' '+ \
                                rub_isk.get(lst_tys[1]+lst_tys[2])+' тысяч'
                    elif lst_tys[1] == '0' and lst_tys[2] != '0':
                        tmp_r = tmp_r+rub_sot.get(lst_tys[0])+' '+rub_tys.get(lst_tys[2])
                    elif lst_tys[1] == '0' and lst_tys[2] == '0':
                        tmp_r = tmp_r+rub_sot.get(lst_tys[0])+' тысяч'
                    else:
                        tmp_r = tmp_r+rub_sot.get(lst_tys[0])+' '+ \
                                rub_des.get(lst_tys[1])+' '+rub_tys.get(lst_tys[2])
                else:
                    if lst_tys[1] == '1':
                        tmp_r = tmp_r+rub_isk.get(lst_tys[1]+lst_tys[2])+' тысяч'
                    elif lst_tys[1] == '0' and lst_tys[2] != '0':
                        tmp_r = tmp_r+rub_tys.get(lst_tys[2])
                    elif lst_tys[1] == '0' and lst_tys[2] == '0':
                        tmp_r = tmp_r
                    else:
                        tmp_r = tmp_r+rub_des.get(lst_tys[1])+ \
                                ' '+rub_tys.get(lst_tys[2])
            tmp_r = tmp_r+' '

        #составляем последний кусок
        if lst_ed != [] and lst_ed != ['0', '0', '0']:
            if len(lst_ed) == 1:
                tmp_r = tmp_r+rub_ed.get(lst_ed[0])
            elif len(lst_ed) == 2:
                if lst_ed[0] == '1':
                    tmp_r = tmp_r+rub_isk.get(lst_ed[0]+lst_ed[1])+' рублей'
                else:
                    tmp_r = tmp_r+rub_des.get(lst_ed[0])+' '+rub_ed.get(lst_ed[1])
            elif len(lst_ed) == 3:
                if lst_ed[0] != '0':
                    if lst_ed[1] == '1':
                        tmp_r = tmp_r+rub_sot.get(lst_ed[0])+' '+ \
                                rub_isk.get(lst_ed[1]+lst_ed[2])+' рублей'
                    elif lst_ed[1] == '0' and lst_ed[2] != '0':
                        tmp_r = tmp_r+rub_sot.get(lst_ed[0])+' '+rub_ed.get(lst_ed[2])
                    elif lst_ed[1] == '0' and lst_ed[2] == '0':
                        tmp_r = tmp_r+rub_sot.get(lst_ed[0])+' рублей'
                    else:
                        tmp_r = tmp_r+rub_sot.get(lst_ed[0])+' '+ \
                                rub_des.get(lst_ed[1])+' '+rub_ed.get(lst_ed[2])
                else:
                    if lst_ed[1] == '1':
                        tmp_r = tmp_r+rub_isk.get(lst_ed[1]+lst_ed[2])+' рублей'
                    elif lst_ed[1] == '0' and lst_ed[2] != '0':
                        tmp_r = tmp_r+rub_ed.get(lst_ed[2])
                    elif lst_ed[1] == '0' and lst_ed[2] == '0':
                        tmp_r = tmp_r+' рублей'
                    else:
                        tmp_r = tmp_r+rub_des.get(lst_ed[1])+ \
                                ' '+rub_ed.get(lst_ed[2])
        elif lst_ed == ['0', '0', '0']:
            tmp_r = tmp_r+'рублей'

        #составляем кусок с копейками
        if len(kop_lst) == 1:
            tmp_k = kop+'0 копеек'
        elif len(kop_lst) == 2:
            if kop_lst[0] != '1':
                tmp_k = kop+' '+kop_ed.get(kop_lst[1], 'копеек')
            else:
                tmp_k = kop+' копеек'

    except ValueError, x:
        print 'Не могу представить сумму прописью!', x

    tmp = tmp_r+' '+tmp_k #объединяем рубли с копейками
    tmp_lst = list(tmp)
    tmp_lst[0] = str(tmp_lst[0]).upper() #делаем первую букву заглавной
    tmp = ''.join(tmp_lst)
    return tmp

import re

def validateEmail(email):
    if len(email) > 7:
        if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) is not None:
            return 1
    return 0

def rus_month(month):
    if month not in xrange(1, 13):
        return ''

    month_val = [u'января', u'февраля', u'марта', u'апреля', u'мая', u'июня', u'июля', u'августа', u'сентября', u'октября', u'ноября', u'декабря']
    return month_val[month - 1]

from django.core.validators import email_re

def is_valid_email(email):
    return True if email_re.match(email) else False