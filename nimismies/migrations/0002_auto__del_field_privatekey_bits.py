# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'PrivateKey.bits'
        db.delete_column(u'nimismies_privatekey', 'bits')


    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'PrivateKey.bits'
        raise RuntimeError("Cannot reverse this migration. 'PrivateKey.bits' and its values cannot be restored.")

    models = {
        u'nimismies.caserial': {
            'Meta': {'object_name': 'CASerial'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'serial_number': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'subject': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '1024'})
        },
        u'nimismies.certificate': {
            'Meta': {'object_name': 'Certificate'},
            '_issuer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['nimismies.Certificate']", 'null': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.utcnow'}),
            'data': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['nimismies.User']", 'null': 'True'}),
            'private_key': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['nimismies.PrivateKey']", 'null': 'True'})
        },
        u'nimismies.certificatesigningrequest': {
            'Meta': {'object_name': 'CertificateSigningRequest'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.utcnow'}),
            'data': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['nimismies.User']"}),
            'private_key': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['nimismies.PrivateKey']", 'null': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'new'", 'max_length': '32'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '1024'})
        },
        u'nimismies.privatekey': {
            'Meta': {'object_name': 'PrivateKey'},
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