# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Comestible.is_dish'
        db.delete_column('food_comestible', 'is_dish')

    def backwards(self, orm):
        # Adding field 'Comestible.is_dish'
        db.add_column('food_comestible', 'is_dish',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)

    models = {
        'food.amount': {
            'Meta': {'object_name': 'Amount'},
            'contained_comestible': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'containing_dishes_set'", 'to': "orm['food.Comestible']"}),
            'containing_dish': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'contained_comestibles_set'", 'to': "orm['food.Dish']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'quantity': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '8', 'decimal_places': '2', 'blank': 'True'})
        },
        'food.comestible': {
            'Meta': {'object_name': 'Comestible'},
            'child_model': ('django.db.models.fields.CharField', [], {'default': "'D'", 'max_length': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'unit': ('django.db.models.fields.CharField', [], {'default': "'g'", 'max_length': '5'})
        },
        'food.dish': {
            'Meta': {'object_name': 'Dish', '_ormbases': ['food.Comestible']},
            'comestible_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['food.Comestible']", 'unique': 'True', 'primary_key': 'True'}),
            'date_cooked': ('django.db.models.fields.DateField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'quantity': ('django.db.models.fields.DecimalField', [], {'default': '500', 'null': 'True', 'max_digits': '8', 'decimal_places': '2', 'blank': 'True'}),
            'total_quantity': ('django.db.models.fields.DecimalField', [], {'default': '500', 'null': 'True', 'max_digits': '8', 'decimal_places': '2', 'blank': 'True'})
        },
        'food.eating': {
            'Meta': {'object_name': 'Eating'},
            'comestible': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['food.Comestible']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'meal': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['food.Meal']"}),
            'quantity': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '8', 'decimal_places': '2', 'blank': 'True'})
        },
        'food.ingredient': {
            'Meta': {'object_name': 'Ingredient', '_ormbases': ['food.Comestible']},
            'calories': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'}),
            'comestible_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['food.Comestible']", 'unique': 'True', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'quantity': ('django.db.models.fields.DecimalField', [], {'default': '100', 'max_digits': '8', 'decimal_places': '2'}),
            'reference_quantity': ('django.db.models.fields.DecimalField', [], {'default': '100', 'max_digits': '8', 'decimal_places': '2'})
        },
        'food.meal': {
            'Meta': {'object_name': 'Meal'},
            'comestibles': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['food.Comestible']", 'through': "orm['food.Eating']", 'symmetrical': 'False'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'time': ('django.db.models.fields.TimeField', [], {})
        }
    }

    complete_apps = ['food']