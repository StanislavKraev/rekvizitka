# -*- coding: utf-8 -*-
class ContactTypeDoesNotExistException(Exception):
    pass

class CantAddOneContact(Exception):
    pass

class CantDeleteOneContact(Exception):
    pass

class CantFindOneContact(Exception):
    pass

class CantUpdateOneContact(Exception):
    pass

class CantSaveContact(Exception):
    pass

class CantAddOneMessage(Exception):
    pass

class CantDeleteOneMessage(Exception):
    pass

class CantUpdateOneMessage(Exception):
    pass

class CantFindOneMessage(Exception):
    pass

class CantSaveMessage(Exception):
    pass

class CantSendMessageNobody(Exception):
    pass

class CantAddUserSettings(Exception):
    pass

class CantUpdateMessageSettings(Exception):
    pass

class CantAddMessageSettings(Exception):
    pass

class CantSaveSettings(Exception):
    pass