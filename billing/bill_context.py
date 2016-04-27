# -*- coding: utf-8 -*-
from django.conf import settings

bill_default_context = {
    'recipient': {        
        'name': 'ООО "РЕК1.РУ"',
        'address': '192102, Санкт-Петербург, ул. Салова, д.55, корп. 5, лит. А',
        'rekvizitka_link': 'http://%s/2A82' % settings.SITE_DOMAIN_NAME,
        'account': '30101810000000000201',
        'account_name': 'ИНН/КПП 7816469431/781601001 ООО "РЕК1.РУ"',
        'bank': {
            'name': 'ОАО АКБ "Авангард" г.Москва',
            'bik': '044525201',
            'account': '40702810802890008194',
        },
    },
    'bill': {
        'number': 'кц-6',
        'date': '24.09.2009',
        'position': 'Регистрация в информационной системе',
        'sum': {
            'in_digits': '1000',
            'in_words': 'одна тысяча рублей 00 копеек',
        },
        'duration': '30 банковских дней'
    },
    'payer': {
        'name': 'ООО "ИНРУСКОМ"',
    }
}

bill_default_context_html = bill_default_context
bill_default_context_pdf = bill_default_context.copy()
bill_default_context_pdf['pdf_optimization'] = True
