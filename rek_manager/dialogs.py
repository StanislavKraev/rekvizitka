# -*- coding: utf-8 -*-

from Tkinter import *
from datetime import datetime
from random import choice
import string
from django.contrib.auth.hashers import PBKDF2PasswordHasher
from django.utils import timezone
from django.utils.encoding import smart_str
from rekvizitka.models import StaffSizeEnum

_hasher = PBKDF2PasswordHasher()

class NewCompanyDialog:
    def __init__(self, parent, user_collection, employee_collection,
                 company_collection, profile_files_grid, profile_logos_collection):
        self.user_collection = user_collection
        self.employee_collection = employee_collection
        self.company_collection = company_collection
        self.profile_logos_collection = profile_logos_collection

        self.profile_files_grid = profile_files_grid

        top = self.top = Toplevel(parent)
        top.geometry('500x600')

        Label(top, text="------- Пользователь --------").grid(row=0, column=0, sticky=E+W)

        Label(top, text="User email").grid(row=1, column=0, sticky=E)
        self.email = Entry(top, width="40")
        self.email.grid(row=1, column=1)

        Label(top, text="Password").grid(row=2, column=0, sticky=E)
        self.password = Entry(top, width="40")
        self.password.grid(row=2, column=1)

        Label(top, text="Activated").grid(row=3, column=0, sticky=E)
        self.is_activated = BooleanVar()
        self.activated = Checkbutton(top, width="40", variable=self.is_activated)
        self.activated.grid(row=3, column=1)
        self.is_activated.set(True)

        Label(top, text="------- Сотрудник --------").grid(row=4, column=0, sticky=E+W)

        Label(top, text="Имя").grid(row=5, column=0, sticky=E)
        self.first_name = Entry(top, width="40")
        self.first_name.grid(row=5, column=1)

        Label(top, text="Фамилия").grid(row=6, column=0, sticky=E)
        self.second_name = Entry(top, width="40")
        self.second_name.grid(row=6, column=1)

        Label(top, text="Отчество").grid(row=7, column=0, sticky=E)
        self.middle_name = Entry(top, width="40")
        self.middle_name.grid(row=7, column=1)

        Label(top, text="Должность").grid(row=8, column=0, sticky=E)
        self.title = Entry(top, width="40")
        self.title.grid(row=8, column=1)

        Label(top, text="Телефон").grid(row=9, column=0, sticky=E)
        self.employee_phone = Entry(top, width="40")
        self.employee_phone.grid(row=9, column=1)

        Label(top, text="------- Компания --------").grid(row=15, column=0, sticky=E+W)

        Label(top, text="Название бренда").grid(row=16, column=0, sticky=E)
        self.brand_name = Entry(top, width="40")
        self.brand_name.grid(row=16, column=1)

        Label(top, text="Краткое наименование").grid(row=17, column=0, sticky=E)
        self.short_name = Entry(top, width="40")
        self.short_name.grid(row=17, column=1)

        Label(top, text="Полное наименование").grid(row=18, column=0, sticky=E)
        self.full_name = Entry(top, width="40")
        self.full_name.grid(row=18, column=1)

        Label(top, text="Описание").grid(row=19, column=0, sticky=E)
        self.description = Text(top,height=4,width=40,background='white')
        self.description.grid(row=19, column=1)

        Label(top, text="Rek id").grid(row=20, column=0, sticky=E)
        self.rek_id = Entry(top, width="40")
        self.rek_id.grid(row=20, column=1)

        b = Button(top, text="Create Account", command=self.ok)
        b.grid(row=40, column=0, sticky=W+E)

    def put_logo_file(self):
        with open('company_logo.jpg', 'rb') as company_logo:
            return self.profile_files_grid.put(company_logo, filename="logo", content_type="image/jpeg")

    def put_micro_logo_file(self, file_name):
        with open(file_name, 'rb') as file:
            return self.profile_files_grid.put(file, filename="comment_logo", content_type="image/jpeg")

    def upload_contact_maps(self):
        maps = []
        chars = string.letters + string.digits
        with open('map.jpg', 'rb') as file:
            random_hash = ''.join([choice(chars) for i in xrange(10)])
            file_name = "contact_map%s" % random_hash
            id = self.profile_files_grid.put(file, filename=file_name, content_type="image/jpeg")
            self.profile_logos_collection.update({'_id' : id}, {'$set' : {'rek_id' : self.rek_id.get()}})
            maps.append(file_name)

        with open('map.jpg', 'rb') as file:
            random_hash = ''.join([choice(chars) for i in xrange(10)])
            file_name = "contact_map%s" % random_hash
            id = self.profile_files_grid.put(file, filename=file_name, content_type="image/jpeg")
            self.profile_logos_collection.update({'_id' : id}, {'$set' : {'rek_id' : self.rek_id.get()}})
            maps.append(file_name)

        return maps

    def ok(self):
        password = smart_str(self.password.get())
        salt = smart_str(_hasher.salt())

        password = _hasher.encode(password, salt)

        bank_account = {'bank' : "Промсвязьбанк",
                        'bank_address' : "Россия. Москва. Красная пл.",
                        'inn' : "012345678912",
                        'bik' : "012345678912345",
                        'correspondent_account' : "0123456789123456789",
                        'settlement_account' : "4123456789123456789",
                        'recipient' : "Иванов Иван Иваныч"}

        user_id = self.user_collection.insert({'email' : self.email.get(),
                                           'password' : password,
                                           'is_active' : True,
                                           'last_login' : timezone.now(),
                                           'date_joined' : timezone.now(),
                                           'activated' : self.is_activated.get()})

        employee_id = self.employee_collection.insert({'user_id' : user_id,
                                                  'first_name' : self.first_name.get(),
                                                  'second_name' : self.second_name.get(),
                                                  'middle_name' : self.middle_name.get(),
                                                  'title' : self.title.get(),
                                                  'phone' : self.employee_phone.get(),
                                                  'male' : True,
                                                  'birth_date' : datetime(2000, 12, 12),
                                                  'profile_status' : "active",
                                                  'deleted' : False,
                                                  'timezone' : "Europe/Moscow"})

        logo_file_id = self.put_logo_file()

        contractors = [{
                'rek_id' : 'CK1',
                'brand_name' : 'Contractor 1',
                'micro_logo' : self.put_micro_logo_file('micro_logo.jpg')
            },
                {
                'rek_id' : 'CK2',
                'brand_name' : 'Contractor 2',
                'micro_logo' : self.put_micro_logo_file('micro_logo2.jpg')
            },
                {
                'rek_id' : 'CK3',
                'brand_name' : 'Contractor 3',
                'micro_logo' : self.put_micro_logo_file('micro_logo3.jpg')
            }
        ]

        contact_maps = self.upload_contact_maps()

        offices = [{
            'city' : 'Гадюкино',
            'information' : 'РФ, Гадюкино, ул. Гадская, д. 0, оф. 9132',
            'physical_address ' : 'РФ, Гадюкино, ул. Гадская, д. 0, оф. 9132',
            'phones' : '+7 (000) 1110011',
            'fax' : None,
            'skype' : 'skype',
            'email' : 'mail@mail.ru',
            'map_img' : {'dim' : (200, 100), 'filename' : contact_maps[0]}
        },{
            'city' : 'Подмышкино',
            'information' : 'РФ, Подмышкино, ул. Большая Мышка, д. 3, оф. 4',
            'physical_address ' : 'РФ, Подмышкино, ул. Большая Мышка, д. 3, оф. 4',
            'phones' : '+7 (001) 0001100',
            'skype' : 'skype',
            'icq' : '13',
            'email' : 'mail@mail.ru',
            'map_img' : {'dim' : (350, 110), 'filename' : contact_maps[1]}
        }]

        company_id = self.company_collection.insert({'rek_id' : self.rek_id.get(),
                                                    'owner_employee_id' : employee_id,
                                                    'short_name' : self.short_name.get(),
                                                    'full_name' : self.full_name.get(),
                                                    'brand_name' : self.brand_name.get(),
                                                    'description' : self.description.get(1.0, END),
                                                    'inc_form' : 13,
                                                    'inn' : '012345678901',
                                                    'kpp' : '012345678',
                                                    'category_text' : 'category',
                                                    'date_creation' : timezone.now(),
                                                    'date_established' : timezone.now(),
                                                    'staff_size' : StaffSizeEnum.RANGE_10_20,
                                                    'options' :{'employee' : False},
                                                    'gen_director' : 'Сидор Егорович Петров',
                                                    'chief_accountant' : 'Максимилиана Чурчхеловна Сидорова-Егорова',
                                                    'account_status' : 'verified',
                                                    'is_account_activated' : self.is_activated.get(),

                                                    'web_sites' : ['abc.ru'],
                                                    'phones' : ['112'],
                                                    'emails' : ['company@mail.ru'],
                                                    'offices' : offices,
                                                    'bank_accounts' : [bank_account],
                                                    'logo_file_id' : logo_file_id,
                                                    'contractors' : contractors
                                                    })

        self.employee_collection.update({'_id' : employee_id}, {'$set' : {'company_id' : company_id}})
        self.profile_logos_collection.update({'_id' : logo_file_id}, {'$set' : {'rek_id' : self.rek_id.get()}})
        rek_id = self.rek_id.get()
        for contra in contractors:
            id = contra['micro_logo']
            self.profile_logos_collection.update({'_id' : id}, {'$set' : {'rek_id' : contra['rek_id']}})

        self.top.destroy()
