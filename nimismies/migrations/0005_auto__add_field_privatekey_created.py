# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'PrivateKey.created'
        db.add_column(u'nimismies_privatekey', 'created',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'PrivateKey.created'
        db.delete_column(u'nimismies_privatekey', 'created')


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
            'data': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['nimismies.User']"})
        },
        u'nimismies.privatekey': {
            'Meta': {'object_name': 'PrivateKey'},
            'bits': ('django.db.models.fields.IntegerField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
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