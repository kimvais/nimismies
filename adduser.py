#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Nimismies adduser tool
Usage: adduser.py [<email>] [<dn>]
"""
import getpass
import docopt

from nimismies.models import User

if __name__ == '__main__':
    args = docopt.docopt(__doc__)
    email = args.pop('<email>', None)
    dn = args.pop('<dn>', None)
    if email is None:
        email = raw_input('Username (e-mail address): ').strip()
    try:
        u = User.objects.get(email=email)
    except User.DoesNotExist:
        u = None
    if u is not None:
        raise RuntimeError('User <{0}> already exists'.format(email))
    if dn is None:
        dn = 'CN={0}/emailAddress={1}'.format(getpass.getuser(), email)
    password = getpass.getpass()
    u = User.objects.create_user(email, dn)
    u.set_password(password)
    u.save()


