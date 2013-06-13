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

from django.contrib.auth.views import logout
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.views.generic import TemplateView, View, FormView, ListView

import M2Crypto
from nimismies import forms, models


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
    template_name = 'create_private_key.html'
    success_url = '/'

    def form_valid(self, form):
        alg = form.cleaned_data.get('key_type', 'dsa')
        size = form.cleaned_data.get('key_size', 2048)
        print(type(size))
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
        # print(public.getvalue())
        # print(private.getvalue())
        private_key = models.PrivateKey()
        private_key.data = private.getvalue()
        private_key.public_key = public.getvalue()
        private_key.owner = self.request.user
        private_key.bits = size
        private_key.key_type = alg
        private_key.save()
        return super(FormView, self).form_valid(form)


class ObjectList(ListView):
    template_name = 'list.html'

    def dispatch(self, request, *args, **kwargs):
        self.choice = kwargs.pop('choice', None)
        return super(ObjectList, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return self.get_model_class().objects.filter(owner=self.request.user)

    def get_model_class(self):
        if self.choice == "private_key":
            return models.PrivateKey
        else:
            raise RuntimeError("Unknown choice {0}".format(self.choice))

    def get_context_data(self, **kwargs):
        ctx = super(ObjectList, self).get_context_data(**kwargs)
        ctx.update(dict(
            choice = self.choice
        ))
        return ctx

