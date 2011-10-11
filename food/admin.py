from food.models import Ingredient, Dish, Amount, Meal, Eating
from django.contrib import admin

class IngredientAdmin(admin.ModelAdmin):
    fields = ['name', 'calories', 'quantity', 'unit']
    search_fields = ['name']

admin.site.register(Ingredient, IngredientAdmin)


class DishAdmin(admin.ModelAdmin):
    fields = ['name', 'date_cooked', 'quantity', 'unit']
    search_fields = ['name', 'date_cooked']

admin.site.register(Dish, DishAdmin)


class AmountAdmin(admin.ModelAdmin):
    fields = ['contained_comestible', 'quantity', 'containing_dish']
    search_fields = ['contained_comestible', 'containing_dish']

admin.site.register(Amount, AmountAdmin)


class MealAdmin(admin.ModelAdmin):
    fields = ['name', 'date', 'time']

admin.site.register(Meal, MealAdmin)

