# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Comestible'
        db.create_table('food_comestible', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('food', ['Comestible'])

        # Adding model 'Ingredient'
        db.create_table('food_ingredient', (
            ('comestible_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['food.Comestible'], unique=True, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200)),
            ('reference_quantity', self.gf('django.db.models.fields.DecimalField')(default=100, max_digits=6, decimal_places=2)),
            ('reference_quantity_unit', self.gf('django.db.models.fields.CharField')(default='g', max_length=5)),
            ('calories', self.gf('django.db.models.fields.DecimalField')(max_digits=6, decimal_places=2)),
        ))
        db.send_create_signal('food', ['Ingredient'])

        # Adding model 'Dish'
        db.create_table('food_dish', (
            ('comestible_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['food.Comestible'], unique=True, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('total_quantity', self.gf('django.db.models.fields.DecimalField')(max_digits=6, decimal_places=2, blank=True)),
            ('total_quantity_unit', self.gf('django.db.models.fields.CharField')(default='g', max_length=5)),
            ('date_cooked', self.gf('django.db.models.fields.DateField')()),
        ))
        db.send_create_signal('food', ['Dish'])

        # Adding model 'Amount'
        db.create_table('food_amount', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('containing_dish', self.gf('django.db.models.fields.related.ForeignKey')(related_name='contained_comestibles_set', to=orm['food.Dish'])),
            ('contained_comestible', self.gf('django.db.models.fields.related.ForeignKey')(related_name='containing_dishes_set', to=orm['food.Comestible'])),
            ('quantity', self.gf('django.db.models.fields.DecimalField')(max_digits=6, decimal_places=2, blank=True)),
        ))
        db.send_create_signal('food', ['Amount'])


    def backwards(self, orm):
        
        # Deleting model 'Comestible'
        db.delete_table('food_comestible')

        # Deleting model 'Ingredient'
        db.delete_table('food_ingredient')

        # Deleting model 'Dish'
        db.delete_table('food_dish')

        # Deleting model 'Amount'
        db.delete_table('food_amount')


    models = {
        'food.amount': {
            'Meta': {'object_name': 'Amount'},
            'contained_comestible': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'containing_dishes_set'", 'to': "orm['food.Comestible']"}),
            'containing_dish': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'contained_comestibles_set'", 'to': "orm['food.Dish']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'quantity': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '2', 'blank': 'True'})
        },
        'food.comestible': {
            'Meta': {'object_name': 'Comestible'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'food.dish': {
            'Meta': {'object_name': 'Dish', '_ormbases': ['food.Comestible']},
            'comestible_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['food.Comestible']", 'unique': 'True', 'primary_key': 'True'}),
            'date_cooked': ('django.db.models.fields.DateField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'total_quantity': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '2', 'blank': 'True'}),
            'total_quantity_unit': ('django.db.models.fields.CharField', [], {'default': "'g'", 'max_length': '5'})
        },
        'food.ingredient': {
            'Meta': {'object_name': 'Ingredient', '_ormbases': ['food.Comestible']},
            'calories': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '2'}),
            'comestible_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['food.Comestible']", 'unique': 'True', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'reference_quantity': ('django.db.models.fields.DecimalField', [], {'default': '100', 'max_digits': '6', 'decimal_places': '2'}),
            'reference_quantity_unit': ('django.db.models.fields.CharField', [], {'default': "'g'", 'max_length': '5'})
        }
    }

    complete_apps = ['food']
