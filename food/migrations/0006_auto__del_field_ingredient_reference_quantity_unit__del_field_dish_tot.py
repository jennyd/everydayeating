# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'Ingredient.reference_quantity_unit'
        db.delete_column('food_ingredient', 'reference_quantity_unit')

        # Deleting field 'Dish.total_quantity_unit'
        db.delete_column('food_dish', 'total_quantity_unit')


    def backwards(self, orm):
        
        # Adding field 'Ingredient.reference_quantity_unit'
        db.add_column('food_ingredient', 'reference_quantity_unit', self.gf('django.db.models.fields.CharField')(default='g', max_length=5), keep_default=False)

        # Adding field 'Dish.total_quantity_unit'
        db.add_column('food_dish', 'total_quantity_unit', self.gf('django.db.models.fields.CharField')(default='g', max_length=5), keep_default=False)


    models = {
        'food.amount': {
            'Meta': {'object_name': 'Amount'},
            'contained_comestible': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'containing_dishes_set'", 'to': "orm['food.Comestible']"}),
            'containing_dish': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'contained_comestibles_set'", 'to': "orm['food.Dish']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'quantity': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '6', 'decimal_places': '2', 'blank': 'True'})
        },
        'food.comestible': {
            'Meta': {'object_name': 'Comestible'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'unit': ('django.db.models.fields.CharField', [], {'default': "'g'", 'max_length': '5'})
        },
        'food.dish': {
            'Meta': {'object_name': 'Dish', '_ormbases': ['food.Comestible']},
            'comestible_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['food.Comestible']", 'unique': 'True', 'primary_key': 'True'}),
            'date_cooked': ('django.db.models.fields.DateField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'total_quantity': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '2', 'blank': 'True'})
        },
        'food.eating': {
            'Meta': {'object_name': 'Eating'},
            'comestible': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['food.Comestible']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'meal': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['food.Meal']"}),
            'quantity': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '2'})
        },
        'food.ingredient': {
            'Meta': {'object_name': 'Ingredient', '_ormbases': ['food.Comestible']},
            'calories': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '2'}),
            'comestible_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['food.Comestible']", 'unique': 'True', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'reference_quantity': ('django.db.models.fields.DecimalField', [], {'default': '100', 'max_digits': '6', 'decimal_places': '2'})
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
