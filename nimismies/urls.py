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

from django.conf.urls import patterns, url
from django.contrib.auth.views import login
from django.contrib.auth.decorators import login_required
from django.views.generic import RedirectView
from nimismies import views

urlpatterns = patterns(
    '',
    url(r'^login', login, name="login"),
    url(r'^logout', views.LogOut.as_view(), name="logout"),
    url(r'^$', login_required(views.Home.as_view()), name='home'),
    url(r'^accounts/profile/', RedirectView.as_view(url='/')),
    url(r'^create/key/', login_required(views.CreatePrivateKey.as_view()),
        name='create_private_key'),
    url(r'^create/csr/', login_required(views.CreateCSR.as_view()),
        name='create_csr'),
    url(r'^upload/csr/', login_required(views.UploadCSR.as_view()),
        name='upload_csr'),
    url(r'^sign/(?P<pk>\d+)/', login_required(views.SignCSR.as_view()),
        name='sign_csr'),
    url(r'^list/(?P<choice>csr)/?', login_required(views.CSRList.as_view()),
        name="list"),
    url(r'^list/(?P<choice>private_key)/?',
        login_required(views.PrivateKeyList.as_view()), name="list"),
    url(r'^list/(?P<choice>certificate)/?',
        login_required(views.CertificateList.as_view()), name="list"),
    url(r'^download/certificate/(?P<pk>\d+)/?',
        views.DownloadCertificate.as_view(),
        name="download_certificate"),
    url(r'^certificate/(?P<pk>\d+)/?',
        login_required(views.Certificate.as_view()),
        name="certificate"),
    # url(r'^nimismies/', include('nimismies.foo.urls')),
)
