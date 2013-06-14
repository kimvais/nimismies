#
# -*- coding: utf-8 -*-
#
# Copyright © 2013 Kimmo Parviainen-Jalanko <k@77.fi>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import datetime
import M2Crypto
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from . import fields


class UserManager(BaseUserManager):
    def create_user(self, email, dn, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=email,
            dn=dn,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    dn = models.CharField(max_length=1024, unique=True, db_index=True)
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
        db_index=True,
    )

    USERNAME_FIELD = 'email'
    objects = UserManager()
    is_staff = True

    def get_full_name(self):
        return self.dn

    def get_short_name(self):
        return self.email


class PrivateKey(models.Model):
    owner = models.ForeignKey('nimismies.User')
    data = fields.EncryptedCharField(null=False,
                                     passphrase_setting='SECRET_KEY',
                                     max_length=8192)
    public_key = models.TextField()
    bits = models.IntegerField()
    key_type = models.CharField(max_length=16)
    created = models.DateTimeField(default=datetime.datetime.utcnow)

    def get_m2_key(self, md='sha1'):
        if self.key_type != 'rsa':
            raise RuntimeWarning('Not a RSA key')
        _rsa_key = M2Crypto.RSA.load_key_string(self.data)
        key = M2Crypto.EVP.PKey(md=md)
        key.assign_rsa(_rsa_key)
        return key

    def __unicode__(self):
        return '{bits}-bit {key_type} key #{id} for <{0}>'.format(
            self.owner, **self.__dict__)


class Certificate(models.Model):
    owner = models.ForeignKey('nimismies.User', null=True)
    issuer = models.ForeignKey('nimismies.Certificate',
                               null=True)  # null means self-signed
    data = models.TextField(null=False)
    created = models.DateTimeField(default=datetime.datetime.utcnow)
    private_key = models.ForeignKey('nimismies.PrivateKey', null=True)

    def __unicode__(self):
        if self.issuer is None:
            issuer = self.owner.dn
        else:
            issuer = self.issuer.dn
        return '{0} signed by {1}'.format(self.owner.dn, issuer)

class CertificateSigningRequest(models.Model):
    owner = models.ForeignKey('nimismies.User')
    created = models.DateTimeField(default=datetime.datetime.utcnow)
    data = models.TextField(null=False)
    subject = models.CharField(max_length=1024)
    status = models.CharField(max_length=32, default="new")
    private_key = models.ForeignKey('nimismies.PrivateKey', null=True)


class CASerial(models.Model):
    subject = models.CharField(max_length=1024, unique=True)
    serial_number = models.IntegerField(default=0)
