# -*- coding: utf-8 -*-

import sys, os

sys.path.append('/home/skraev/djangostack/python/lib/python2.6/site-packages/')
sys.path.append('/home/skraev/projects/')
sys.path.append('D:/rekvizitka/rek')
sys.path.append('D:/rekvizitka')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from Tkinter import *
from gridfs import GridFS
from rek.rek_manager.panels import CompanyControlPanel, CompanyEmployeeControlPanel, UsersControlPanel, CompanyProfileFilesControlPanel
from django.contrib.auth.hashers import PBKDF2PasswordHasher
from pymongo import Connection

connection = Connection(host='127.0.0.1', port=27017, tz_aware=True)
mongodb = connection['rekvizitka']

users_collection = mongodb['users']
employee_collection = mongodb['company_employees']
company_collection = mongodb['companies']
profile_logos_collection = mongodb['company_profile_files.files']

profile_files_grid = GridFS(mongodb, 'company_profile_files')

_hasher = PBKDF2PasswordHasher()

class UsersDecorator(object):
    def handle(self, item):
        return "%s activated:%s" % (item['email'], item['activated'])

class App:

    def __init__(self, master):
        self.decorators = {}
        self.control_panels = {}
        self.collection_names = []
        self.data_items = []
        self.panel = None

        for name in mongodb.collection_names():
            if name.startswith('system.'):
                continue
            self.collection_names.append(name)

        frame = Frame(master)
        frame.pack(fill="both", expand=True, side=LEFT)

        frame_top = Frame(frame)
        frame_top.pack(fill="x", expand=True, side=TOP)

        self.frame_bottom = Frame(frame)
        self.frame_bottom.pack(fill="x", expand=True, side=BOTTOM)

        self.data_type_listbox = Listbox(frame_top)
        self.data_type_listbox.pack(side=LEFT, fill="x", expand=True, )
        self.data_type_listbox['height'] = 30

        for item in self.collection_names:
            self.data_type_listbox.insert(END, item)

        self.data_type_listbox.bind('<<ListboxSelect>>', self.on_type_selected)

        self.data_list_listbox = Listbox(frame_top)
        self.data_list_listbox.pack(side=RIGHT, fill="x", expand=True)
        self.data_list_listbox['height'] = 30

        self.data_list_listbox.bind('<<ListboxSelect>>', self.on_item_selected)

        self.init_control_panels()

    def init_control_panels(self):
        self.add_control_panel('users', UsersControlPanel(self.frame_bottom, users_collection, employee_collection,
                                                          company_collection, profile_files_grid, profile_logos_collection))
        self.add_control_panel('companies', CompanyControlPanel(self.frame_bottom, company_collection))
        self.add_control_panel('company_employees', CompanyEmployeeControlPanel(self.frame_bottom, employee_collection))
        self.add_control_panel('company_profile_files.files',
                               CompanyProfileFilesControlPanel(self.frame_bottom, profile_logos_collection, profile_files_grid))

    def on_type_selected(self, event):
        selection = event.widget.curselection()
        collection_name = self.collection_names[int(selection[0])]
        self.data_items = []

        if self.panel:
            self.panel.replace()
        new_panel = self.control_panels.get(collection_name)
        if new_panel:
            self.panel = new_panel
            self.panel.place()

        items = mongodb[collection_name].find()

        self.data_list_listbox.delete(0, END)
        index = 1
        for item in items:
            try:
                self.data_list_listbox.insert(END, "%d. %s" % (index, self.decorate_item(collection_name, item)))
                self.data_items.append(item)
            except Exception, ex:
                print(ex)
            index += 1

        self.data_list_listbox.select_set(0)
        self.data_list_listbox.activate(0)

    def on_item_selected(self, event):
        selection = event.widget.curselection()
        data = self.data_items[int(selection[0])]
        if self.panel:
            self.panel.set_data(data)

    def decorate_item(self, collection_name, item):
        decorator = self.decorators.get(collection_name)
        if not decorator:
            return str(item)
        return decorator.handle(item)

    def add_decorator(self, collection_name, decorator):
        self.decorators[collection_name] = decorator

    def add_control_panel(self, collection_name, panel):
        self.control_panels[collection_name] = panel

root = Tk()

app = App(root)
root.geometry("800x600")

app.add_decorator('users', UsersDecorator())

root.mainloop()