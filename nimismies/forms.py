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
from contextlib import closing
import os
import tempfile
import traceback
import M2Crypto

from django import forms
from nimismies import models


class PrivateKey(forms.Form):
    key_type = forms.ChoiceField(choices=(
        ('rsa', 'RSA'),), # ('dsa', 'DSA'), ('ecdsa', 'EC DSA'),),
                                 widget=forms.Select(
                                     attrs={'class': 'radio'}),
                                 initial="rsa"
    )

    key_size = forms.ChoiceField(choices=(
        (1024, '1024 bits'), (2048, '2048 bits'), (4096, '4096 bits'),),
                                 widget=forms.Select(
                                     attrs={'class': 'radio'}),
                                 initial=2048)

    def clean_key_size(self):
        return int(self.data['key_size'])


class PrivateKeySelectionForm(forms.Form):
    private_key = forms.ChoiceField(widget=forms.Select(choices=(None, None)))

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(PrivateKeySelectionForm, self).__init__(*args, **kwargs)
        print(self.user)
        self.fields['private_key'].choices = list(
            (key.pk,
             '{0}-bit {1} key #{2}'.format(
                 key.bits,
                 key.key_type.upper(),
                 key.pk)) for key in
            models.PrivateKey.objects.filter(
                owner=self.user))


class CSR(PrivateKeySelectionForm):
    subject = forms.CharField(max_length=1024)

    def __init__(self, *args, **kwargs):
        super(CSR, self).__init__(*args, **kwargs)
        self.fields['subject'].initial = self.user.dn


class SignCSR(forms.Form):
    issuer = forms.ChoiceField(choices=(None,))

    def __init__(self, *args, **kwargs):
        choices = list()
        private_key = kwargs.pop('private_key', None)
        user = kwargs.pop('user', None)
        if private_key is not None:
            choices.append(('SELF', "Self-signed"))
        choices.extend((cert.pk, str(cert))
                       for cert in models.Certificate.objects.exclude(
            private_key=None).filter(owner=user))
        super(SignCSR, self).__init__(*args, **kwargs)
        self.fields['issuer'].choices = choices


class CSRUpload(forms.Form):
    paste = forms.CharField(widget=forms.Textarea(
        attrs={'width': '95%'}), required=False, )
    upload = forms.FileField(required=False)

    def clean(self):
        if not self.cleaned_data['paste'] and not self.files:
            raise forms.ValidationError("Must either paste or upload a "
                                        "request")
        if self.cleaned_data['paste']:
            data = str(self.cleaned_data['paste'])
        else:
            data = str(self.files['upload'].read())
        fd, fpath = tempfile.mkstemp()
        with closing(os.fdopen(fd, 'r+')) as csr_file:
            csr_file.write(data)
            csr_file.seek(0)
            try:
                M2Crypto.X509.load_request(fpath)
            except Exception as e:
                print(e)
                traceback.print_exc()
                raise forms.ValidationError("Malformed certificate singing "
                                            "request")
            finally:
                os.remove(fpath)
        return dict(csr=data)

