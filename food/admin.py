from food.models import Ingredient
from django.contrib import admin

class IngredientAdmin(admin.ModelAdmin):
    fields = ['name', 'calories', 'reference_quantity', 'reference_quantity_unit', 'clagginess']
    search_fields = ['name']

admin.site.register(Ingredient, IngredientAdmin)
