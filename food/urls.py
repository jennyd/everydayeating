from django.conf.urls.defaults import *
from django.views.generic import simple, list_detail, create_update # deprecated function-based generic views
from django.views.generic import base, ListView # new class-based generic views
from food.models import Ingredient, Dish, Amount

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


#### not used now - using class-based generic ListView
#ingredient_info = {
#    "queryset" : Ingredient.objects.all().order_by("name"),
#    "template_object_name" : "ingredient",
#}

# using ingredient_add_info for edit too - same options for now
ingredient_add_info = {
    "model" : Ingredient,
    "post_save_redirect" : "/food/ingredients/",
}

dish_info = {
    "queryset" : Dish.objects.all().order_by("date_cooked"),
    "template_object_name" : "dish",
}

ingredient_detail_info = {
    "queryset" : Ingredient.objects.all(),
    "template_object_name" : "ingredient",
}

#### not used now - using generic view through dish_detail_with_amounts instead
#dish_detail_info = {
#    "queryset" : Dish.objects.all(),
#    "template_object_name" : "dish",
#    "extra_context" : {"amounts" : get_amounts},
#}


# first versions of my views
urlpatterns = patterns('food.views',
    # Example:
    # (r'^everydayeating/', include('everydayeating.foo.urls')),
#    (r'^ingredients/$', 'ingredient_index'),
#    (r'^ingredients/(?P<ingredient_id>\d+)/$', 'ingredient_detail'),
#    url(r'^ingredients/(?P<ingredient_id>\d+)/edit/$', 'ingredient_edit', name="ingredient_edit"),
#    url(r'^ingredients/(?P<ingredient_id>\d+)/edit/thanks/$', 'ingredient_edit_thanks', name="ingredient_edit_thanks"),
#    url(r'^ingredients/add/$', 'ingredient_add', name="ingredient_add"),
#    url(r'^ingredients/add/thanks/$', 'ingredient_add_thanks', name="ingredient_add_thanks"),
#    (r'^dishes/$', 'dish_index'),
    url(r'^dishes/(?P<dish_id>\d+)/$', 'dish_detail_with_amounts', name="dish_detail"),
    url(r'^dishes/(?P<dish_id>\d+)/edit/$', 'dish_edit', name="dish_edit"),
    url(r'^dishes/(?P<dish_id>\d+)/edit/(?P<amount_id>\d+)/$', 'amount_edit', name="amount_edit"),
    url(r'^dishes/(?P<dish_id>\d+)/edit/thanks/$', 'dish_edit_thanks', name="dish_edit_thanks"),
    url(r'^dishes/(?P<dish_id>\d+)/edit/(?P<amount_id>\d+)/thanks/$', 'amount_edit_thanks', name="amount_edit_thanks"),
)

# using old function-based generic views
urlpatterns += patterns('',
#    url(r'^$', simple.direct_to_template, { 'template' : 'food/food_index.html' }, "food_index"),
#    url(r'^ingredients/$', list_detail.object_list, kwargs=ingredient_info, name="ingredient_list"),
    url(r'^ingredients/add/$', create_update.create_object, kwargs=ingredient_add_info, name="ingredient_add"),
    url(r'^ingredients/(?P<object_id>\d+)/$', list_detail.object_detail, kwargs=ingredient_detail_info, name="ingredient_detail"),
    url(r'^ingredients/(?P<object_id>\d+)/edit/$', create_update.update_object, kwargs=ingredient_add_info, name="ingredient_edit"),
    url(r'^dishes/$', list_detail.object_list, kwargs=dish_info, name="dish_list"),
#    url(r'^dishes/(?P<object_id>\d+)/$', list_detail.object_detail, kwargs=dish_detail_info, name="dish_detail"),
)

# using new class-based generic views
urlpatterns += patterns('',
    url(r'^$', base.TemplateView.as_view(template_name='food/food_index.html'), name="food_index"),
    url(r'^ingredients/$', ListView.as_view( queryset=Ingredient.objects.all().order_by("name") ), name="ingredient_list"),
)
