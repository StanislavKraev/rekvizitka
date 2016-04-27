# -*- coding: utf-8 -*-

import re
from rek.mango import Model, database as db
from django.utils.encoding import smart_str
from django.contrib.auth.models import SiteProfileNotAvailable
from django.contrib.auth.hashers import UNUSABLE_PASSWORD, PBKDF2PasswordHasher, is_password_usable
from django.utils import timezone
import urllib
from rek.mongo.models import SimpleModel, ObjectManager

_hasher = PBKDF2PasswordHasher()

class User(Model):
    collection = db.users

    def __unicode__(self):
        return self.email

    def get_absolute_url(self):
        return "/users/%s/" % urllib.quote(smart_str(self.username))

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True

    def make_password(self, password):
        if not password:
            return UNUSABLE_PASSWORD

        password = smart_str(password)
        salt = smart_str(_hasher.salt())

        return _hasher.encode(password, salt)


    def set_password(self, raw_password):
        self.password = self.make_password(raw_password)

    def check_password_cmp(self, password, encoded):
        """
        Returns a boolean of whether the raw password matches the three
        part encoded digest.

        If setter is specified, it'll be called when you need to
        regenerate the password.
        """
        if not password or not is_password_usable(encoded):
            return False

        password = smart_str(password)
        encoded = smart_str(encoded)

        return _hasher.verify(password, encoded)

    def check_password(self, raw_password):
        return self.check_password_cmp(raw_password, self.password)

    def set_unusable_password(self):
        self.password = UNUSABLE_PASSWORD

    def has_usable_password(self):
        return self.password != UNUSABLE_PASSWORD

    def get_group_permissions(self):
        return []
#        permissions = set()
#        for backend in auth.get_backends():
#            if hasattr(backend, "get_group_permissions"):
#                permissions.update(backend.get_group_permissions(self))
#        return permissions

    def get_all_permissions(self):
        return []
#        permissions = set()
#        for backend in auth.get_backends():
#            if hasattr(backend, "get_all_permissions"):
#                permissions.update(backend.get_all_permissions(self))
#        return permissions

    def has_perm(self, perm):
        return True
#        if not self.is_active:
#            return False
#
#        if self.is_superuser:
#            return True
#
#        for backend in auth.get_backends():
#            if hasattr(backend, "has_perm"):
#                if backend.has_perm(self, perm):
#                    return True
#        return False

    def has_perms(self, perm_list):
#        for perm in perm_list:
#            if not self.has_perm(perm):
#                return False
        return True

    def has_module_perms(self, app_label):
        return True
#        if not self.is_active:
#            return False
#
#        if self.is_superuser:
#            return True
#
#        for backend in auth.get_backends():
#            if hasattr(backend, "has_module_perms"):
#                if backend.has_module_perms(self, app_label):
#                    return True
#        return False

    def get_and_delete_messages(self):
        return []

#    def email_user(self, subject, message, from_email=None):
#        from django.core.mail import send_mail
#        send_mail(subject, message, from_email, [self.email])

    def get_profile(self):
        raise SiteProfileNotAvailable

    @classmethod
    def create_user(cls, email, password=None):
        """Creates and saves a User with the given username, e-mail and password."""
        now = timezone.now()
        user = cls({'email': email.strip().lower(), # same as login
                    'password': 'placeholder',
                    'is_active': True,
                    'last_login': now,
                    'date_joined': now,
                    'activated' : False
                    })
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        try:
            user.save(safe=True)
        except Exception:
            return None
        return user

    @classmethod
    def find_one(cls, kwargs):
        return cls.collection.find_one(kwargs)

    @classmethod
    def make_random_password(cls, length=10, allowed_chars='abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789'):
        """Generates a random password with the given length and given allowed_chars"""
        # Note that default value of allowed_chars does not have "I" or letters
        # that look like it -- just to avoid confusion.
        from random import choice
        return ''.join([choice(allowed_chars) for i in range(length)])

    @classmethod
    def set_indexes(cls):
        cls.collection.ensure_index('email', unique=True)

User.set_indexes()

class AnonymousUser(object):
    id = None
    username = ''
    is_staff = False
    is_active = False
    is_superuser = False
#    _groups = EmptyManager()
#    _user_permissions = EmptyManager()

    def __init__(self):
        pass

    def __unicode__(self):
        return 'AnonymousUser'

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __eq__(self, other):
        return isinstance(other, self.__class__)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return 1 # instances always return the same hash value

    def save(self):
        raise NotImplementedError

    def delete(self):
        raise NotImplementedError

    def set_password(self, raw_password):
        raise NotImplementedError

    def check_password(self, raw_password):
        raise NotImplementedError

    def _get_groups(self):
        #return self._groups
        return []
    groups = property(_get_groups)

    #def _get_user_permissions(self):
        #return self._user_permissions
        #return []
    #user_permissions = property(_get_user_permissions)

    def get_group_permissions(self, obj=None):
        return set()

    def get_all_permissions(self, obj=None):
        #return _user_get_all_permissions(self, obj=obj)
        return set()

    def has_perm(self, perm, obj=None):
        #return _user_has_perm(self, perm, obj=obj)
        return True

    def has_perms(self, perm_list, obj=None):
#        for perm in perm_list:
#            if not self.has_perm(perm, obj):
#                return False
#        return True
        return True

    def has_module_perms(self, module):
#        return _user_has_module_perms(self, module)
        return True

    def get_and_delete_messages(self):
        return []

    def is_anonymous(self):
        return True

    def is_authenticated(self):
        return False


class Backend(object):
    """
    Authenticates against a mongodb 'users' collection.
    """
    supports_inactive_user = False

    def authenticate(self, username=None, password=None):
        user = User.get({'email': username})
        if user:
            if user.check_password(password):
                return user
        return None

    def get_user(self, user_id):
        return User.get({'_id': user_id})

class UserActivationLinks(SimpleModel):
    def __init__(self, kwargs = None):
        kwargs = kwargs or {}
        self._id = kwargs.get('_id')
        self.user = kwargs.get('user')
        self.created = kwargs.get('created', timezone.now())

    def _fields(self):
        return {'user' : self.user,
                'created' : self.created}

UserActivationLinks.objects = ObjectManager(UserActivationLinks, 'user_activation_links', [('user', 1),
    ('created', -1)])

def get_password_error(password):
    if len(password) < 6:
        return u'Некорректный пароль. Минимальная длина 6 символов.'
    if not re.match(r"^[a-zA-Z0-9-&*!@#%^()_]+$", password):
        return u'Некорректный пароль. Недопустимый символ.'
    return None