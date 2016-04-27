# -*- coding: utf-8 -*-
from datetime import timedelta

import os, sys
from django.utils import timezone

CUR_FOLDER = os.path.dirname(__file__)
sys.path.append(os.path.join(CUR_FOLDER, '..'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from rek.chat.models import ChatDialog, DialogMessage
from rek.mango.auth import User
from rek.rekvizitka.models import CompanyEmployee, Company

def register_companies(count=1, verified=False):
    companies = []
    employees = []
    users = []

    for i in xrange(count):
        email = 'testemail%i@testdomain.zz' % i
        rek_id = 'CCC%i' % i
        password = 'password'
        brand_name = u'Порошки%i' % i

        created_user = User.create_user(email, password)
        if not created_user:
            raise Exception('failed to create user')

        new_employee = CompanyEmployee({'user_id':created_user._id,
                                        'timezone' : 'Europe/Moscow'})
        new_employee.save()

        new_company = Company({'rek_id':rek_id,
                               'owner_employee_id':new_employee._id,
                               'brand_name' : brand_name,
                               'is_account_activated' : True,
                               'date_creation' : timezone.now() + timedelta(days=i)})
        if verified:
            new_company.account_status = 'verified'

        new_company.save()
        new_employee.set(company_id=new_company._id)

        users.append(created_user)
        employees.append(new_employee)
        companies.append(new_company)

    User.collection.update({}, {'$set' : {'activated' : True, 'is_active' : True}}, multi=True)
    return companies, employees, users


def get_company_employee(company):
    return CompanyEmployee.objects.get_one({'company_id' : company._id})

def create_chat_dialog(employee_from, employee_to):
    new_dialog = ChatDialog({'parties' : [employee_from._id, employee_to._id],
                             'creator' : employee_from._id})
    new_dialog.save()
    return new_dialog

def send_chat_messages(dialog, message_count = 1, text = 'abc'):
    for i in xrange(message_count):
        msg_text = text + str(i)

        new_message = DialogMessage({'dialog' : dialog._id,
                                     'text' : msg_text,
                                     'creator' : dialog.creator})
        new_message.save()
        ChatDialog.objects.collection.update({'_id' : dialog._id}, {'$set' : {
            'last_message_date' : new_message.date,
            'last_message_text' : new_message.text[:200],
            'last_message_party' : dialog.creator,
            'last_message_id' : new_message._id,
            'hidden_by_parties' : [],
            'not_viewed_by_parties' : dialog.parties
        }})

def main():
    companies = register_companies(10, verified=True)[0]
    my_company = companies[0]
    my_employee = get_company_employee(my_company)
    for company in companies[1:]:
        employee = get_company_employee(company)
        dialog = create_chat_dialog(my_employee, employee)
        send_chat_messages(dialog, 10, text="preved medved")

main()