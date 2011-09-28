# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'Ingredient.clagginess'
        db.delete_column('food_ingredient', 'clagginess')

        # Deleting field 'Dish.clagginess'
        db.delete_column('food_dish', 'clagginess')


    def backwards(self, orm):
        
        # Adding field 'Ingredient.clagginess'
        db.add_column('food_ingredient', 'clagginess', self.gf('django.db.models.fields.CharField')(default='', max_length=1, blank=True), keep_default=False)

        # Adding field 'Dish.clagginess'
        db.add_column('food_dish', 'clagginess', self.gf('django.db.models.fields.CharField')(default='', max_length=1, blank=True), keep_default=False)


    models = {
        'food.amount': {
            'Meta': {'object_name': 'Amount'},
            'containing_dish': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'contained_amounts_set'", 'to': "orm['food.Dish']"}),
            'dish_as_ingredient': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'amounts_using_set'", 'null': 'True', 'to': "orm['food.Dish']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ingredient': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['food.Ingredient']", 'null': 'True', 'blank': 'True'}),
            'quantity': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '2', 'blank': 'True'})
        },
        'food.dish': {
            'Meta': {'object_name': 'Dish'},
            'date_cooked': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'total_quantity': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '2', 'blank': 'True'}),
            'total_quantity_unit': ('django.db.models.fields.CharField', [], {'default': "'g'", 'max_length': '5'})
        },
        'food.ingredient': {
            'Meta': {'object_name': 'Ingredient'},
            'calories': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'reference_quantity': ('django.db.models.fields.DecimalField', [], {'default': '100', 'max_digits': '6', 'decimal_places': '2'}),
            'reference_quantity_unit': ('django.db.models.fields.CharField', [], {'default': "'g'", 'max_length': '5'})
        }
    }

    complete_apps = ['food']
