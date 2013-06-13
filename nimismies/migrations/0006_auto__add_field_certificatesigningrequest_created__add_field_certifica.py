# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'CertificateSigningRequest.created'
        db.add_column(u'nimismies_certificatesigningrequest', 'created',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.utcnow),
                      keep_default=False)

        # Adding field 'CertificateSigningRequest.subject'
        db.add_column(u'nimismies_certificatesigningrequest', 'subject',
                      self.gf('django.db.models.fields.CharField')(default='CN=kimvais', max_length=1024),
                      keep_default=False)

        # Adding field 'CertificateSigningRequest.status'
        db.add_column(u'nimismies_certificatesigningrequest', 'status',
                      self.gf('django.db.models.fields.CharField')(default='new', max_length=32),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'CertificateSigningRequest.created'
        db.delete_column(u'nimismies_certificatesigningrequest', 'created')

        # Deleting field 'CertificateSigningRequest.subject'
        db.delete_column(u'nimismies_certificatesigningrequest', 'subject')

        # Deleting field 'CertificateSigningRequest.status'
        db.delete_column(u'nimismies_certificatesigningrequest', 'status')


    models = {
        u'nimismies.certificate': {
            'Meta': {'object_name': 'Certificate'},
            'data': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issuer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['nimismies.Certificate']"}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['nimismies.User']"})
        },
        u'nimismies.certificatesigningrequest': {
            'Meta': {'object_name': 'CertificateSigningRequest'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.utcnow'}),
            'data': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['nimismies.User']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'new'", 'max_length': '32'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '1024'})
        },
        u'nimismies.privatekey': {
            'Meta': {'object_name': 'PrivateKey'},
            'bits': ('django.db.models.fields.IntegerField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.utcnow'}),
            'data': ('nimismies.fields.EncryptedCharField', ["'SECRET_KEY'", '8192'], {'null': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key_type': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['nimismies.User']"}),
            'public_key': ('django.db.models.fields.TextField', [], {})
        },
        u'nimismies.user': {
            'Meta': {'object_name': 'User'},
            'dn': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '1024', 'db_index': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        }
    }

    complete_apps = ['nimismies']