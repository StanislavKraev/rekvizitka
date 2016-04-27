# -*- coding: utf-8 -*-

from Tkinter import *
from rek.rek_manager.dialogs import NewCompanyDialog

class CommonPanel(object):
    def __init__(self, parent_widget):
        self.frame = Frame(parent_widget)
        self.data = None

    def place(self):
        self.frame.pack(expand=True, fill="both")

    def replace(self):
        self.frame.pack_forget()

    def set_data(self, data):
        self.data = data

class CompanyControlPanel(CommonPanel):
    def __init__(self, parent_widget, company_collection):
        super(CompanyControlPanel, self).__init__(parent_widget)
        self.company_collection = company_collection
        drop_company_button = Button(self.frame, text="Уничтожить Компанию", command=self.drop_company)
        drop_company_button.pack(side=LEFT)

    def drop_company(self):
        self.company_collection.remove(self.data['_id'])

class CompanyEmployeeControlPanel(CommonPanel):
    def __init__(self, parent_widget, employee_collection):
        super(CompanyEmployeeControlPanel, self).__init__(parent_widget)
        self.employee_collection = employee_collection
        drop_button = Button(self.frame, text="Уничтожить Сотрудника", command=self.drop_employee)
        drop_button.pack(side=LEFT)

    def drop_employee(self):
        self.employee_collection.remove(self.data['_id'])

class UsersControlPanel(CommonPanel):
    def __init__(self, parent_widget, users_collection,
                 employee_collection, company_collection, profile_files_grid, profile_logos_collection):
        super(UsersControlPanel, self).__init__(parent_widget)

        self.users_collection = users_collection
        self.employee_collection = employee_collection
        self.company_collection = company_collection
        self.profile_files_grid = profile_files_grid
        self.profile_logos_collection = profile_logos_collection

        create_account_button = Button(self.frame, text="Создать Аккаунт", command=self.create_account)
        create_account_button.pack(side=LEFT)

        drop_account_button = Button(self.frame, text="Уничтожить Аккаунт", command=self.drop_account)
        drop_account_button.pack(side=LEFT)

    def create_account(self):
        NewCompanyDialog(self.frame, self.users_collection,
            self.employee_collection,
            self.company_collection,
            self.profile_files_grid,
            self.profile_logos_collection)

    def drop_account(self):
        employee = self.employee_collection.find_one({'user_id' : self.data['_id']})
        if employee:
            self.company_collection.remove(employee['company_id'])
            self.employee_collection.remove(employee['_id'])
        self.users_collection.remove(self.data['_id'])

class CompanyProfileFilesControlPanel(CommonPanel):
    def __init__(self, parent_widget, profile_logos_collection, profile_files_grid):
        super(CompanyProfileFilesControlPanel, self).__init__(parent_widget)
        self.profile_logos_collection = profile_logos_collection
        self.profile_files_grid = profile_files_grid
        drop_company_button = Button(self.frame, text="Уничтожить файлы", command=self.drop)
        drop_company_button.pack(side=LEFT)

    def drop(self):
        for file in self.profile_logos_collection.find({}):
            self.profile_files_grid.delete(file['_id'])
