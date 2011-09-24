from django.conf.urls.defaults import *
from django.views.generic import simple, list_detail
from food.models import Ingredient, Dish

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

ingredient_info = {
    "queryset" : Ingredient.objects.all().order_by("name"),
    "template_object_name" : "ingredient",
}

dish_info = {
    "queryset" : Dish.objects.all().order_by("date_cooked"),
    "template_object_name" : "dish",
}

ingredient_detail = {
    "queryset" : Ingredient.objects.all(),
    "template_object_name" : "ingredient",
#    "object_id" : "ingredient_id",
}

urlpatterns = patterns('food.views',
    # Example:
    # (r'^everydayeating/', include('everydayeating.foo.urls')),
#    (r'^ingredients/$', 'ingredient_index'),
#    (r'^ingredients/(?P<ingredient_id>\d+)/$', 'ingredient_detail'),
    (r'^ingredients/(?P<ingredient_id>\d+)/edit/$', 'ingredient_edit'),
    (r'^ingredients/(?P<ingredient_id>\d+)/edit/thanks/$', 'ingredient_edit_thanks'),
    (r'^ingredients/add/$', 'ingredient_add'),
    (r'^ingredients/add/thanks/$', 'ingredient_add_thanks'),
#    (r'^dishes/$', 'dish_index'),
    (r'^dish/(?P<dish_id>\d+)/$', 'dish_detail'),
    (r'^dishes/(?P<dish_id>\d+)/edit/$', 'dish_edit'),
    (r'^dishes/(?P<dish_id>\d+)/edit/(?P<amount_id>\d+)/$', 'amount_edit'),
    (r'^dishes/(?P<dish_id>\d+)/edit/thanks/$', 'dish_edit_thanks'),
)

urlpatterns += patterns('',
    (r'^$', simple.direct_to_template, {'template': 'food/food_index.html'}),
    (r'^ingredients/$', list_detail.object_list, ingredient_info),
    (r'^dishes/$', list_detail.object_list, dish_info),
    (r'^ingredients/(?P<object_id>\d+)/$', list_detail.object_detail, ingredient_detail),
)

