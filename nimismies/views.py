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
import logging
import os
import subprocess
import tempfile
from contextlib import closing

from django.contrib.auth.views import logout
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, View, FormView, ListView

import M2Crypto
import time
from jsforms.decorators import jsform
from nimismies import forms, models

logger = logging.getLogger(__name__)


class Home(TemplateView):
    template_name = "base.html"

    def get_context_data(self, **kwargs):
        ctx = super(TemplateView, self).get_context_data(**kwargs)
        return ctx


class LogOut(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect(reverse('login'))


class CreatePrivateKey(FormView):
    form_class = forms.PrivateKey
    template_name = 'create.html'
    success_url = '/list/private_key/'

    def form_valid(self, form):
        alg = form.cleaned_data.get('key_type', 'dsa')
        size = form.cleaned_data.get('key_size', 2048)
        logger.debug(type(size))
        private = M2Crypto.BIO.MemoryBuffer()
        public = M2Crypto.BIO.MemoryBuffer()
        if alg == "dsa":
            key = M2Crypto.DSA.gen_params(size)
            key.gen_key()
        elif alg == "ecdsa":
            # TODO: Implement this
            CURVES = dict()
            key = M2Crypto.EC.gen_params(CURVES[size])
            key.gen_key()
        elif alg == "rsa":
            key = M2Crypto.RSA.gen_key(size, 65537)
        else:
            raise RuntimeError('Invalid algorithm {0}'.format(alg))
        key.save_key_bio(private, cipher=None)
        key.save_pub_key_bio(public)
        # logger.debug(public.getvalue())
        # logger.debug(private.getvalue())
        private_key = models.PrivateKey()
        private_key.data = private.getvalue()
        private_key.public_key = public.getvalue()
        private_key.owner = self.request.user
        private_key.bits = size
        private_key.key_type = alg
        private_key.save()
        return super(FormView, self).form_valid(form)


class FormViewWithUser(FormView):
    def get_form_kwargs(self):
        kwargs = super(FormViewWithUser, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

def set_name_from_string(dn_string, name=None):
    if name is None:
        name = M2Crypto.X509.X509_Name
    for field in dn_string:
        attr, value = field.split('=', 1)
        setattr(name, attr, value)
    return name

class CreateCSR(FormViewWithUser):

    form_class = forms.CSR
    template_name = 'create.html'

    success_url = '/list/csr/'

    def form_valid(self, form):
        logger.debug(form.cleaned_data)
        logger.debug(form.cleaned_data)
        data = form.cleaned_data
        pk = models.PrivateKey.objects.get(pk=data['private_key'])
        fd, fpath = tempfile.mkstemp()
        logger.debug(fpath)
        csr = M2Crypto.X509.Request()
        name = csr.get_subject()
        set_name_from_string(data['subject'].split('/'), name)
        csr.set_subject_name(name)
        with closing(os.fdopen(fd, 'r+')) as keyfile:
            keyfile.write(pk.public_key)
            keyfile.seek(0)
            if pk.key_type == "rsa":
                public_key = M2Crypto.RSA.load_pub_key(fpath)
                os.remove(fpath)
                pkey = M2Crypto.EVP.PKey(md='sha1')
                pkey.assign_rsa(public_key)
                csr.set_pubkey(pkey)
            elif pk.key_type == "dsa":
                raise NotImplementedError(
                    "CSRs for DSA keys is unimplemented due lack of M2Crypto"
                    " wrappers")
            else:
                raise RuntimeError("Invalid key algorithm {0}".format(
                    pk.key_type))
        logger.debug(name.as_text())
        csr_o = models.CertificateSigningRequest(data=csr.as_pem(),
                                                 owner=self.request.user)
        csr_o.subject = name.as_text()
        csr_o.save()
        return super(FormView, self).form_valid(form)


class ObjectList(ListView):
    def get_template_names(self):
        return ['{0}_list.html'.format(self.choice)]

    def dispatch(self, request, *args, **kwargs):
        self.choice = kwargs.pop('choice', None)
        return super(ObjectList, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return self.get_model_class().objects.filter(owner=self.request.user)

    def get_model_class(self):
        if self.choice == "private_key":
            return models.PrivateKey
        elif self.choice == "csr":
            return models.CertificateSigningRequest
        elif self.choice == "certificate":
            return models.Certificate
        else:
            raise RuntimeError("Unknown choice {0}".format(self.choice))

    def get_context_data(self, **kwargs):
        ctx = super(ObjectList, self).get_context_data(**kwargs)
        ctx.update(dict(
            choice=self.choice
        ))
        return ctx


class SignCSR(FormViewWithUser):
    form_class = forms.SignCSR
    template_name = "create.html"
    success_url = '/list/certificate/'

    @method_decorator(jsform())
    def dispatch(self, request, *args, **kwargs):
        self.csr = models.CertificateSigningRequest.objects.get(
            pk=kwargs.pop('pk'))
        return super(SignCSR, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        data = form.cleaned_data
        years = data.get('years', 3)
        logger.debug(data)
        pk_o = models.PrivateKey.objects.get(pk=data['private_key'])
        if pk_o.key_type != 'rsa':
            raise NotImplementedError("Only RSA keys can be used for signing"
                                      " at the moment")
        _private_key = M2Crypto.RSA.load_key_string(pk_o.data)
        private_key = M2Crypto.EVP.PKey(md='sha1')
        private_key.assign_rsa(_private_key)
        with open('/tmp/mycsr.csr', 'w') as f:
            f.write(self.csr.data)
        logger.debug(subprocess.check_output(
            'openssl req -in /tmp/mycsr.csr -noout -text'.split()))
        csr = M2Crypto.X509.load_request('/tmp/mycsr.csr')
        logger.debug(private_key)
        logger.debug(csr)
        # Calculate validity period
        t_start = long(time.time()) + time.timezone
        t_end = t_start + 86400 * 365 * years
        valid_from = M2Crypto.ASN1.ASN1_UTCTIME()
        valid_from.set_time(t_start)
        valid_until = M2Crypto.ASN1.ASN1_UTCTIME()
        valid_until.set_time(t_end)
        issuer = csr.get_subject()
        public_key = csr.get_pubkey()
        logger.debug(public_key)
        # Generate the actual certificate
        certificate = M2Crypto.X509.X509()
        certificate.set_version(0)
        certificate.set_not_before(valid_from)
        certificate.set_not_after(valid_until)
        certificate.set_pubkey(public_key)
        certificate.set_issuer(issuer)
        certificate.set_subject(issuer)
        certificate.sign(private_key, md='sha1')
        crt = models.Certificate()
        owner = models.User.objects.get(dn=certificate.get_subject().as_text())
        crt.owner = owner
        crt.issuer = None
        crt.data = certificate.as_pem()
        crt.save()

        return super(SignCSR, self).form_valid(form)
