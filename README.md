# nimismies

This project aims to be easy-to-deploy certificate authority (CA) with a web based UI. It will run on Django and OpenSSL (via M2Crypto)

## Instructions

### Installation

1. `git clone git://github.com/kimvais/nimismies.git`
1. `cd nimismies`
1. `make setup`

Make setup does the following:
1. `createdb nimismies`
1. `python manage.py syncdb`
1. `python manage.py migrate nimismies`
1. `./adduser.py <your email address>`

## Features

At the moment _nimismies_ is a minimally functional Certificate authority.

You can:

* Create CA keys (RSA only)
* Create CSRs for CA keys
* Generate self-signed certificates
* Upload CSRs
* Sign CSR using CA keys
* Download certificates

### TODO ###

In addition to the basic CA functionality (issuing Certificates!) I plan on
adding support for OSCP, SCEP and HSMs.

## Versioning

Version number is stored in settings.VERSION

The project is versioned with one form of semantic versioning. Versions are
not decimal, so x.y.9 will probably be followed by x.y.10

For 0.0.x version, each time a new functionality is in _working_ condition,
the 'patch' level will be bumped.

0.1.x will be
the first version that will be at least _remotely_ usable as a CA.
After that, each minor version bump will add actual features aiming for
a 1.0 release at some point in the distant future.

## License

The MIT License

Copyright © 2013 Kimmo Parviainen-Jalanko

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN

