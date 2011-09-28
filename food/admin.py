from food.models import Ingredient, Dish, Amount
from django.contrib import admin

class IngredientAdmin(admin.ModelAdmin):
    fields = ['name', 'calories', 'reference_quantity', 'reference_quantity_unit']
    search_fields = ['name']

admin.site.register(Ingredient, IngredientAdmin)


class DishAdmin(admin.ModelAdmin):
    fields = ['name', 'date_cooked', 'total_quantity', 'total_quantity_unit']
    search_fields = ['name', 'date_cooked']

admin.site.register(Dish, DishAdmin)


class AmountAdmin(admin.ModelAdmin):
    fields = ['contained_comestible', 'quantity', 'containing_dish']
    search_fields = ['contained_comestible', 'containing_dish']

admin.site.register(Amount, AmountAdmin)

