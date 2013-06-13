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
#
# based on http://djangosnippets.org/snippets/2489/
from base64 import b64encode, b64decode

from django.db import models
from django import forms
from django.conf import settings

from M2Crypto import Rand, EVP


def _base64_len(length):
    """Converts a length in 8 bit bytes to a length in 6 bits per byte\
    base64 encoding"""
    # Every 24 bits (3 bytes) becomes 32 bits (4 bytes, 6 bits encoded per byte)
    # End is padded with '=' to make the result a multiple of 4
    units, trailing = divmod(length, 3)
    if trailing:
        units += 1
    return 4 * units


class EncryptedData(str):
    """Used to identify data that has already been encrypted"""


class _FieldCipher(object):
    """Actual cipher engine used to protect the model field"""
    # Could make all these configurable per field, but why?
    _CIPHER_ALG = 'aes_256_cbc'
    _SALT_LEN = 8
    _IV_LEN = 32
    _KEY_LEN = 32

    def __init__(self, passphrase):
        self._passphrase = passphrase # Yuck, but needed for transparent access

    def stored_len(self, max_length):
        """Calculates actual storage needed for a nominal max_length"""
        return _base64_len(self._SALT_LEN + self._IV_LEN + max_length)

    def _make_key(self, salt):
        """Creates a key of the specified length via PBKDF2 (RFC 2898)"""
        return EVP.pbkdf2(self._passphrase, salt, 1000, self._KEY_LEN)

    def _make_encryptor(self, key, iv):
        return EVP.Cipher(alg=self._CIPHER_ALG, key=key, iv=iv, op=1)

    def encrypt(self, plaintext):
        """Encrypts plaintext, returns (salt, iv, ciphertext) tuple"""
        salt = Rand.rand_bytes(self._SALT_LEN)
        key = self._make_key(salt)
        iv = Rand.rand_bytes(self._IV_LEN)
        encryptor = self._make_encryptor(key, iv)
        ciphertext = encryptor.update(plaintext)
        ciphertext += encryptor.final()
        return salt, iv, ciphertext

    def _make_decryptor(self, key, iv):
        return EVP.Cipher(alg=self._CIPHER_ALG, key=key, iv=iv, op=0)

    def decrypt(self, salt, iv, ciphertext):
        """Decrypts ciphertext with given key salt and initvector, returns plaintext"""
        key = self._make_key(salt)
        decryptor = self._make_decryptor(key, iv)
        plaintext = decryptor.update(ciphertext)
        plaintext += decryptor.final()
        return plaintext


class EncryptedCharField(models.CharField):
    """CharField variant that provides transparent encryption

       Accessing encrypted fields requires an attacker compromise not only the
       database, but also either the runtime memory of the web server or the
       settings file (or other mechanism) used to configure the passphrase.

       To support database migrations, the passphrase must be accessible via
       the django.conf.settings namespaces

       WARNING: Do NOT store the passphrase in the same database as the
       encrypted fields as that would defeat the entire point of the
       exercise.
    """
    __metaclass__ = models.SubfieldBase
    _DB_FIELD_PREFIX = "django-encrypted-field:"
    _DB_FIELD_PREFIX_LEN = len(_DB_FIELD_PREFIX)
    _SALT_START = 0
    _IV_START = _SALT_START + _FieldCipher._SALT_LEN
    _CIPHERTEXT_START = _IV_START + _FieldCipher._IV_LEN

    def __init__(self, passphrase_setting, max_length, *args,
                 **kwds):
        passphrase = getattr(settings, passphrase_setting)
        cipher = _FieldCipher(passphrase)
        kwds['max_length'] = (self._DB_FIELD_PREFIX_LEN +
                              cipher.stored_len(max_length))
        super(EncryptedCharField, self).__init__(*args, **kwds)
        self.max_length = max_length
        self._cipher = cipher
        # DB migration support
        self._passphrase_setting = passphrase_setting
        self._south_args = [max_length] + list(args)
        kwds.pop('max_length')
        self._south_kwds = kwds

    def get_prep_lookup(self, lookup_type, value):
        raise Exception('You cannot do lookups on an encrypted field.')

    def get_db_prep_lookup(self, *args, **kw):
        raise Exception('You cannot do lookups on an encrypted field.')

    def get_db_prep_value(self, value, connection, prepared=False):
        """Transparently encrypt and base64 encode data"""
        if isinstance(value, EncryptedData):
            return value
        salt, iv, ciphertext = self._cipher.encrypt(value.encode('ascii'))
        encrypted = salt + iv + ciphertext
        encoded = b64encode(encrypted).decode('ascii')
        with_prefix = self._DB_FIELD_PREFIX + encoded
        return EncryptedData(with_prefix)

    def to_python(self, value):
        """Transparently base64 decode and decrypt data"""
        # Deserialisation (e.g. from admin form) provides a string
        # Database lookup provides... a string
        # So we use an embedded prefix to tell the difference
        # Maybe if my Form-fu was better, I could work out how to get
        # the deserialisation to pass in a different type and get
        # rid of the prefix on the DB side :P
        field_data = super(EncryptedCharField, self).to_python(value)
        has_prefix = field_data.startswith(self._DB_FIELD_PREFIX)
        if has_prefix:
            encoded = field_data[self._DB_FIELD_PREFIX_LEN:]
        elif isinstance(value, EncryptedData):
            encoded = field_data
        else:
            return field_data
        encrypted = b64decode(str(encoded))
        salt = encrypted[self._SALT_START:self._IV_START]
        iv = encrypted[self._IV_START:self._CIPHERTEXT_START]
        ciphertext = encrypted[self._CIPHERTEXT_START:]
        return str(self._cipher.decrypt(salt, iv, ciphertext).decode('ascii'))

    def formfield(self, **kwds):
        defaults = {'widget': forms.PasswordInput(render_value=False),
                    'max_length': self.max_length
        }
        defaults.update(kwds)
        return super(EncryptedCharField, self).formfield(**defaults)

    def south_field_triple(self):
        """Allow the 'south' DB migration tool to handle these fields"""
        qualified_name = self.__module__ + '.' + self.__class__.__name__
        args = [repr(self._passphrase_setting)]
        args += map(repr, self._south_args)
        kwds = {k: repr(v) for k, v in self._south_kwds.items()}
        return qualified_name, args, kwds
