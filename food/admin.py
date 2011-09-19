from food.models import Ingredient, Dish
from django.contrib import admin

class IngredientAdmin(admin.ModelAdmin):
    fields = ['name', 'calories', 'reference_quantity', 'reference_quantity_unit', 'clagginess']
    search_fields = ['name']

admin.site.register(Ingredient, IngredientAdmin)


class DishAdmin(admin.ModelAdmin):
    fields = ['name', 'date_cooked', 'total_quantity', 'total_quantity_unit', 'clagginess']
    search_fields = ['name', 'date_cooked']

admin.site.register(Dish, DishAdmin)

