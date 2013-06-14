# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Certificate.created'
        db.add_column(u'nimismies_certificate', 'created',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.utcnow),
                      keep_default=False)

        # Adding field 'Certificate.private_key'
        db.add_column(u'nimismies_certificate', 'private_key',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nimismies.PrivateKey'], null=True),
                      keep_default=False)

        # Adding field 'CertificateSigningRequest.private_key'
        db.add_column(u'nimismies_certificatesigningrequest', 'private_key',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nimismies.PrivateKey'], null=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Certificate.created'
        db.delete_column(u'nimismies_certificate', 'created')

        # Deleting field 'Certificate.private_key'
        db.delete_column(u'nimismies_certificate', 'private_key_id')

        # Deleting field 'CertificateSigningRequest.private_key'
        db.delete_column(u'nimismies_certificatesigningrequest', 'private_key_id')


    models = {
        u'nimismies.certificate': {
            'Meta': {'object_name': 'Certificate'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.utcnow'}),
            'data': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issuer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['nimismies.Certificate']", 'null': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['nimismies.User']"}),
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