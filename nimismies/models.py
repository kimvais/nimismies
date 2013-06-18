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
from utils import generate_key_fingerprint


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
    key_type = models.CharField(max_length=16)
    created = models.DateTimeField(default=datetime.datetime.utcnow)

    def get_m2_key(self, md='sha1'):
        if not self.data:
            return None
        if self.key_type != 'rsa':
            raise RuntimeWarning('Not a RSA key')
        _rsa_key = M2Crypto.RSA.load_key_string(self.data)
        key = M2Crypto.EVP.PKey(md=md)
        key.assign_rsa(_rsa_key)
        return key

    def __unicode__(self):
        try:
            return '{bits}-bit {key_type} key #{id} for <{owner}>'.format(
                owner=self.owner, bits=self.bits, id=self.pk,
                key_type=self.key_type)
        except:
            return "Private Key #" + str(self.pk)

    def __init__(self, *args, **kwargs):
        super(PrivateKey, self).__init__(*args, **kwargs)
        self.key = self.get_m2_key()

    @property
    def bits(self):
        return self.key.size() * 8



class Certificate(models.Model):
    owner = models.ForeignKey('nimismies.User', null=True)
    _issuer = models.ForeignKey('nimismies.Certificate',
                                null=True)  # null means self-signed
    data = models.TextField(null=False)
    created = models.DateTimeField(default=datetime.datetime.utcnow)
    private_key = models.ForeignKey('nimismies.PrivateKey', null=True)

    def __unicode__(self):
        return '{0} signed by {1}'.format(self.subject, self.issuer)

    def get_m2_certificate(self):
        return M2Crypto.X509.load_cert_string(str(self.data))

    def __init__(self, *args, **kwargs):
        super(Certificate, self).__init__(*args, **kwargs)
        if self.data:
            self.m2_certificate = self.get_m2_certificate()
        else:
            self.m2_certificate = None

    @property
    def issuer(self):
        return self.m2_certificate.get_issuer().as_text()

    @property
    def subject(self):
        return self.m2_certificate.get_subject().as_text()

    @property
    def serial(self):
        return self.m2_certificate.get_serial_number()

    @property
    def sha1_fingerprint(self):
        return self.m2_certificate.get_fingerprint(md='sha1')

    @property
    def sha2_fingerprint(self):
        return self.m2_certificate.get_fingerprint(md='sha256')

    @property
    def validity(self):
        return (self.m2_certificate.get_not_before().get_datetime(),
                self.m2_certificate.get_not_after().get_datetime())

    @property
    def key_id(self):
        return generate_key_fingerprint(self.m2_certificate.get_pubkey().as_der())


class CertificateSigningRequest(models.Model):
    owner = models.ForeignKey('nimismies.User', null=True)
    created = models.DateTimeField(default=datetime.datetime.utcnow)
    data = models.TextField(null=False)
    subject = models.CharField(max_length=1024)
    status = models.CharField(max_length=32, default="new")
    private_key = models.ForeignKey('nimismies.PrivateKey', null=True)

    def __init__(self, *args, **kwargs):
        super(CertificateSigningRequest, self).__init__(*args, **kwargs)
        if self.data:
            bio = M2Crypto.BIO.MemoryBuffer(data=str(self.data))
            self.m2csr = M2Crypto.X509.load_request_bio(bio)
            self.subject = self.m2csr.get_subject().as_text()

    @classmethod
    def from_pem(cls, data):
        self = cls()
        self.data = data
        bio = M2Crypto.BIO.MemoryBuffer(data=str(self.data))
        self.m2csr = M2Crypto.X509.load_request_bio(bio)
        self.subject = self.m2csr.get_subject().as_text()
        return self

    @property
    def public_key(self):
        return self.m2csr.get_pubkey().as_pem()

    @property
    def key_id(self):
        return generate_key_fingerprint(self.m2csr.get_pubkey().as_der())

    @classmethod
    def from_pem(cls, data):
        csr = cls(data=data)
        return csr


class CASerial(models.Model):
    subject = models.CharField(max_length=1024, unique=True)
    serial_number = models.IntegerField(default=0)
