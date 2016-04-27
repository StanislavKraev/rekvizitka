# -*- coding: utf-8 -*-

import sys
import getpass
from optparse import make_option
from django.core import exceptions
from django.contrib.auth.management.commands.createsuperuser import  is_valid_email
from django.core.management.base import BaseCommand, CommandError
from rek.mango.auth import User

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--password', dest='password', default=None,
            help='Specifies password.'),
        make_option('--email', dest='email', default=None,
            help='Specifies the email address for the user.'),
        make_option('--noinput', action='store_false', dest='interactive', default=True,
            help=('Tells Django to NOT prompt the user for input of any kind. '
                  'You must use --email and --password with --noinput.')),
        )
    help = u'Create administration user\n'

    def handle(self, *args, **options):
        email = options.get('email', None)
        password = options.get('password', None)
        interactive = options.get('interactive')
        verbosity = int(options.get('verbosity', 1))

        # Do quick and dirty validation if --noinput
        if not interactive:
            if not password or not email:
                raise CommandError("You must use --password and --email with --noinput.")
            try:
                is_valid_email(email)
            except exceptions.ValidationError:
                raise CommandError("Invalid email address.")
            password = password.strip()
            if not len(password) < 6:
                raise CommandError("Password length must be > 5.")

        # Prompt for username/email/password. Enclose this whole thing in a
        # try/except to trap for a keyboard interrupt and exit gracefully.
        if interactive:
            try:

                # Get an email
                while 1:
                    if not email:
                        email = raw_input('E-mail address: ')
                        email = email.strip().lower()
                    try:
                        is_valid_email(email)
                    except exceptions.ValidationError:
                        sys.stderr.write("Error: That e-mail address is invalid.\n")
                        email = None
                    else:
                        break

                # Get a password
                while 1:
                    if not password:
                        password = getpass.getpass()
                        password2 = getpass.getpass('Password (again): ')
                        if password != password2:
                            sys.stderr.write("Error: Your passwords didn't match.\n")
                            password = None
                            continue
                    if len(password.strip()) < 6:
                        sys.stderr.write("Password length must be > 5.\n")
                        password = None
                        continue
                    break
            except KeyboardInterrupt:
                sys.stderr.write("\nOperation cancelled.\n")
                sys.exit(1)

        email = email.strip().lower()
        try:
            user = User.create_user(email, password)
            User.collection.update({'_id' : user._id}, {'$set' : {'is_superuser' : True}})
        except Exception, ex:
            sys.stderr.write("\nFailed to create user.\n%s\n" % unicode(ex))

        if verbosity >= 1:
            self.stdout.write("Superuser created successfully.\n")

