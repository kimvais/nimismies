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
from __future__ import print_function
import logging
import os
import subprocess
import tempfile
from contextlib import closing
import time

from django.contrib.auth.views import logout
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, View, FormView, ListView, DetailView
import M2Crypto
from pyasn1.codec.der import decoder as der_decoder
from pyasn1_modules import rfc2560

from jsforms.decorators import jsform
from nimismies import forms, models
from utils import new_extension


logger = logging.getLogger(__name__)
logger.debug = print


def empty_callback(_=None):
    pass


class Home(TemplateView):
    template_name = "base.html"

    def get_context_data(self, **kwargs):
        ctx = super(TemplateView, self).get_context_data(**kwargs)
        return ctx


class LogOut(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect(reverse('login'))


class CreateViewMixin(object):
    def get_context_data(self, **kwargs):
        ctx = super(CreateViewMixin, self).get_context_data(**kwargs)
        ctx['button_text'] = 'Create'
        return ctx


class CreatePrivateKey(CreateViewMixin, FormView):
    form_class = forms.PrivateKey
    template_name = 'form.html'
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


class CreateCSR(CreateViewMixin, FormViewWithUser):
    form_class = forms.CSR
    template_name = 'form.html'

    success_url = '/list/csr/'

    def form_valid(self, form):
        logger.debug(form.cleaned_data)
        logger.debug(form.cleaned_data)
        data = form.cleaned_data
        pk = models.PrivateKey.objects.get(pk=data['private_key'])
        csr = M2Crypto.X509.Request()
        name = csr.get_subject()
        set_name_from_string(data['subject'].split('/'), name)
        csr.set_subject_name(name)
        fd, fpath = tempfile.mkstemp()
        with closing(os.fdopen(fd, 'r+')) as keyfile:
            keyfile.write(pk.public_key)
            keyfile.seek(0)
            if pk.key_type == "rsa":
                public_key = M2Crypto.RSA.load_pub_key(fpath)
                os.remove(fpath)
                pkey = M2Crypto.EVP.PKey(md='sha1')
                pkey.assign_rsa(public_key)
                print(pkey.as_pem(cipher=None, callback=empty_callback))
                csr.set_pubkey(pkey)
                print(csr.get_pubkey().as_pem(cipher=None,
                                              callback=empty_callback))
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
        csr_o.private_key = pk
        csr_o.save()
        return super(FormView, self).form_valid(form)


class ObjectList(ListView):
    choice = None

    def get_template_names(self):
        return ['{0}_list.html'.format(self.choice)]

    def get_queryset(self):
        raise RuntimeError('cannot get list of base class')

    def get_context_data(self, **kwargs):
        ctx = super(ObjectList, self).get_context_data(**kwargs)
        ctx.update(dict(
            choice=self.choice
        ))
        return ctx


class PrivateKeyList(ObjectList):
    choice = "private_key"

    def get_queryset(self):
        return models.PrivateKey.objects.filter(owner=self.request.user)


class CertificateList(ObjectList):
    choice = "certificate"

    def get_queryset(self):
        return models.Certificate.objects.all()


class CSRList(ObjectList):
    choice = "csr"

    def get_queryset(self):
        return models.CertificateSigningRequest.objects.exclude(
            status="signed")


class SignCSR(FormViewWithUser):
    form_class = forms.SignCSR
    template_name = "sign.html"
    success_url = '/list/certificate/'

    @method_decorator(jsform())
    def dispatch(self, request, *args, **kwargs):
        self.csr = models.CertificateSigningRequest.objects.get(
            pk=kwargs.pop('pk'))
        fd, fpath = tempfile.mkstemp()
        with closing(os.fdopen(fd, 'r+')) as f:
            f.write(self.csr.data)
        self.csr_text = subprocess.check_output(
            'openssl req -in {0} -noout -text'.format(
                fpath).split()).replace('\t', '  ')
        logger.debug(self.csr_text)
        os.remove(fpath)
        # Set up the keys
        return super(SignCSR, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        data = form.cleaned_data
        years = data.get('years', 3)
        logger.debug(data)
        issuer_id = data['issuer']
        if issuer_id == "SELF":
            self_signed = True
            issuer = self.csr.m2csr.get_subject()
            pk_o = self.csr.private_key
            email = pk_o.owner.email
        else:
            self_signed = False
            issuing_crt = models.Certificate.objects.get(
                pk=issuer_id)
            issuer = issuing_crt.m2_certificate.get_subject()
            pk_o = issuing_crt.private_key
            email = None
        if pk_o.key_type != 'rsa':
            raise NotImplementedError("Only RSA keys can be used for signing"
                                      " at the moment")
        private_key = pk_o.get_m2_key()
        public_key = self.csr.m2csr.get_pubkey()
        logger.debug(public_key)
        logger.debug(private_key)
        # Calculate validity period
        t_start = long(time.time()) + time.timezone
        t_end = t_start + 86400 * 365 * years
        valid_from = M2Crypto.ASN1.ASN1_UTCTIME()
        valid_from.set_time(t_start)
        valid_until = M2Crypto.ASN1.ASN1_UTCTIME()
        valid_until.set_time(t_end)
        # Set serial number both for certificate and the CA
        ca_serial, _ = models.CASerial.objects.get_or_create(
            subject=issuer.as_text())
        ca_serial.serial_number += 1
        ca_serial.save()
        serial = ca_serial.serial_number
        # Generate the actual certificate
        certificate = M2Crypto.X509.X509()
        certificate.set_serial_number(serial)
        certificate.set_version(2)
        certificate.set_not_before(valid_from)
        certificate.set_not_after(valid_until)
        certificate.set_pubkey(public_key)
        certificate.set_issuer(issuer)
        certificate.set_subject(self.csr.m2csr.get_subject())
        # add extensions:
        if data['ca']:
            certificate.add_ext(M2Crypto.X509.new_extension(
                'basicConstraints',
                'CA:TRUE',
                critical=1))
        val = ', '.join(data['key_usage_extensions'])
        logger.debug(val)
        certificate.add_ext(M2Crypto.X509.new_extension(
            'keyUsage',
            val,
            critical=1))
        if email is not None:
            certificate.add_ext(M2Crypto.X509.new_extension('subjectAltName',
                                                            'email:{0}'.format(
                                                                email)))
        certificate.add_ext(M2Crypto.X509.new_extension(
            'subjectKeyIdentifier',
            self.csr.key_id))
        if not self_signed:
            authority_id = 'keyid,issuer:always'
            logger.debug(authority_id)
            certificate.add_ext(new_extension(
                'authorityKeyIdentifier',
                authority_id, issuer=issuing_crt.m2_certificate))
        certificate.sign(private_key, md='sha1')
        if not self_signed:
            # TODO: Configure OCSP distribution point, and save it here.
            certificate.add_ext(M2Crypto.X509.new_extension(
                'authorityInfoAccess', 'OCSP;URI:http://localhost:8000/ocsp/'
            ))
        # M2Crypto Certificate is all set up, let's make a model instance out
        # of it
        crt = models.Certificate()
        crt.owner = self.csr.owner
        crt.data = certificate.as_pem()
        if self_signed:
            crt.private_key = pk_o
        crt.save()
        # and finally mark the CSR as processed
        self.csr.status = "signed"
        self.csr.save()
        return redirect(self.success_url)

    def get_context_data(self, **kwargs):
        ctx = super(SignCSR, self).get_context_data(**kwargs)
        ctx['csr_text'] = self.csr_text
        ctx["button_text"] = "Certify"
        return ctx

    def get_form_kwargs(self):
        kw = super(SignCSR, self).get_form_kwargs()
        kw['user'] = self.request.user
        kw['private_key'] = self.csr.private_key
        return kw


class UploadCSR(FormView):
    form_class = forms.CSRUpload
    success_url = '/list/csr/'
    template_name = 'fileform.html'

    def get_context_data(self, **kwargs):
        ctx = super(UploadCSR, self).get_context_data(**kwargs)
        ctx['button_text'] = 'Upload'
        return ctx

    def form_valid(self, form):
        raw_csr = form.cleaned_data['csr']
        print(raw_csr)
        csr = models.CertificateSigningRequest.from_pem(data=raw_csr)
        bio = M2Crypto.BIO.MemoryBuffer(data=raw_csr)
        req = M2Crypto.X509.load_request_bio(bio)
        csr.subject = req.get_subject().as_text()
        csr.private_key = None
        csr.save()
        return super(UploadCSR, self).form_valid(form)


class DownloadCertificate(View):
    def dispatch(self, request, *args, **kwargs):
        try:
            self.certificate = models.Certificate.objects.get(
                pk=kwargs.pop('pk'))
        except models.Certificate.DoesNotExist:
            raise Http404
        return super(DownloadCertificate, self).dispatch(request, *args,
                                                         **kwargs)

    def get(self, request, *args, **kwargs):
        response = HttpResponse(self.certificate.data)
        response.content_type = 'text/plain'
        response['Content-Disposition'] = 'attachment; certificate.pem'
        return response


class Certificate(DetailView):
    template_name = "certificate_detail.html"
    model = models.Certificate


class OCSP(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(OCSP, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = request.body
        print(['{0:x}'.format(ord(x)) for x in data])
        print( der_decoder.decode(data))
        ocsp_request = der_decoder.decode(data, asn1Spec=rfc2560.OCSPRequest)
        logger.debug(ocsp_request)
        response = HttpResponse()
        return response
