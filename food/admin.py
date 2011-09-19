from food.models import Food
from django.contrib import admin

class FoodAdmin(admin.ModelAdmin):
    fields = ['calories', 'reference_quantity', 'reference_quantity_unit', 'clagginess']
    search_fields = ['name']

admin.site.register(Food, FoodAdmin)
