# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Call'
        db.create_table('football365_call', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('call_type', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('football365_service_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('football365', ['Call'])


    def backwards(self, orm):
        # Deleting model 'Call'
        db.delete_table('football365_call')


    models = {
        'football365.call': {
            'Meta': {'ordering': "('title',)", 'object_name': 'Call'},
            'call_type': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'football365_service_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        }
    }

    complete_apps = ['football365']