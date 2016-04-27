class Permission(object):
    def __init__(self, user, employee = None, company = None):
        self.user = user
        self.employee = employee
        self.company = company
