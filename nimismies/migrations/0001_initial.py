# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'User'
        db.create_table(u'nimismies_user', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('last_login', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('dn', self.gf('django.db.models.fields.CharField')(unique=True, max_length=1024, db_index=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(unique=True, max_length=255, db_index=True)),
        ))
        db.send_create_signal(u'nimismies', ['User'])

        # Adding model 'PrivateKey'
        db.create_table(u'nimismies_privatekey', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nimismies.User'])),
            ('data', self.gf('nimismies.fields.EncryptedCharField')('SECRET_KEY', 8192, null=False)),
            ('public_key', self.gf('django.db.models.fields.TextField')()),
            ('bits', self.gf('django.db.models.fields.IntegerField')()),
            ('key_type', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.utcnow)),
        ))
        db.send_create_signal(u'nimismies', ['PrivateKey'])

        # Adding model 'Certificate'
        db.create_table(u'nimismies_certificate', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nimismies.User'])),
            ('issuer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nimismies.Certificate'], null=True)),
            ('data', self.gf('django.db.models.fields.TextField')()),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.utcnow)),
            ('private_key', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nimismies.PrivateKey'], null=True)),
        ))
        db.send_create_signal(u'nimismies', ['Certificate'])

        # Adding model 'CertificateSigningRequest'
        db.create_table(u'nimismies_certificatesigningrequest', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nimismies.User'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.utcnow)),
            ('data', self.gf('django.db.models.fields.TextField')()),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('status', self.gf('django.db.models.fields.CharField')(default='new', max_length=32)),
            ('private_key', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nimismies.PrivateKey'], null=True)),
        ))
        db.send_create_signal(u'nimismies', ['CertificateSigningRequest'])


    def backwards(self, orm):
        # Deleting model 'User'
        db.delete_table(u'nimismies_user')

        # Deleting model 'PrivateKey'
        db.delete_table(u'nimismies_privatekey')

        # Deleting model 'Certificate'
        db.delete_table(u'nimismies_certificate')

        # Deleting model 'CertificateSigningRequest'
        db.delete_table(u'nimismies_certificatesigningrequest')


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