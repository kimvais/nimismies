# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Certificate'
        db.create_table(u'nimismies_certificate', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nimismies.User'])),
            ('issuer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nimismies.Certificate'])),
            ('data', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'nimismies', ['Certificate'])

        # Adding model 'CertificateSigningRequest'
        db.create_table(u'nimismies_certificatesigningrequest', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nimismies.User'])),
            ('data', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'nimismies', ['CertificateSigningRequest'])

        # Adding model 'PrivateKey'
        db.create_table(u'nimismies_privatekey', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nimismies.User'])),
            ('data', self.gf('nimismies.fields.EncryptedCharField')('SECRET_KEY', 8192, null=False)),
        ))
        db.send_create_signal(u'nimismies', ['PrivateKey'])

        # Adding model 'User'
        db.create_table(u'nimismies_user', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('last_login', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('dn', self.gf('django.db.models.fields.CharField')(unique=True, max_length=1024, db_index=True)),
            ('USERNAME_FIELD', self.gf('django.db.models.fields.EmailField')(unique=True, max_length=75, db_index=True)),
        ))
        db.send_create_signal(u'nimismies', ['User'])


    def backwards(self, orm):
        # Deleting model 'Certificate'
        db.delete_table(u'nimismies_certificate')

        # Deleting model 'CertificateSigningRequest'
        db.delete_table(u'nimismies_certificatesigningrequest')

        # Deleting model 'PrivateKey'
        db.delete_table(u'nimismies_privatekey')

        # Deleting model 'User'
        db.delete_table(u'nimismies_user')


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
            'data': ('nimismies.fields.EncryptedCharField', ["'SECRET_KEY'", '8192'], {'null': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['nimismies.User']"})
        },
        u'nimismies.user': {
            'Meta': {'object_name': 'User'},
            'USERNAME_FIELD': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75', 'db_index': 'True'}),
            'dn': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '1024', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        }
    }

    complete_apps = ['nimismies']