from django.conf.urls.defaults import *
from food.views import ingredient_manage, dish_amounts_form, meal_eating_form
from django.views.generic import TemplateView, ListView, CreateView, DetailView, UpdateView, DeleteView
from food.models import Ingredient, Dish, Amount, Meal, Eating

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('food.views',
    # Example:
    # (r'^everydayeating/', include('everydayeating.foo.urls')),
    url(r'^ingredients/manage/$', "ingredient_manage", name="ingredient_manage"),
    url(r'^dishes/add/$', "dish_amounts_form", name="dish_add"),
    url(r'^dishes/(?P<dish_id>\d+)/edit/ingredients/$', "dish_amounts_form", name="dish_edit_amounts"),
    url(r'^meals/add/$', "meal_eating_form", name="meal_add"),
    url(r'^meals/(?P<meal_id>\d+)/edit/eating/$', "meal_eating_form", name="meal_edit_eating"),
)

urlpatterns += patterns('',
    url(r'^$', TemplateView.as_view( template_name='food/food_index.html' ), name="food_index"),

    url(r'^ingredients/$', ListView.as_view( model=Ingredient ), name="ingredient_list"),
    url(r'^ingredients/add/$', CreateView.as_view( model=Ingredient, success_url="/food/ingredients/" ), name="ingredient_add"),
    url(r'^ingredients/(?P<pk>\d+)/$', DetailView.as_view( model=Ingredient ), name="ingredient_detail"),
    url(r'^ingredients/(?P<pk>\d+)/edit/$', UpdateView.as_view( model=Ingredient, success_url="/food/ingredients/"), name="ingredient_edit"),
    url(r'^ingredients/(?P<pk>\d+)/delete/$', DeleteView.as_view( model=Ingredient, success_url="/food/ingredients/"), name="ingredient_delete"),

    url(r'^dishes/$', ListView.as_view( model=Dish ), name="dish_list"),
#    url(r'^dishes/add/$', CreateView.as_view( model=Dish, success_url="/food/dishes/%(id)s/" ), name="dish_add"),
    url(r'^dishes/(?P<pk>\d+)/$', DetailView.as_view( model = Dish ), name="dish_detail"),
    url(r'^dishes/(?P<pk>\d+)/edit/$', UpdateView.as_view( model=Dish, success_url="/food/dishes/%(id)s/"), name="dish_edit"),
    url(r'^dishes/(?P<dish_id>\d+)/edit/(?P<pk>\d+)/$', UpdateView.as_view( model=Amount, success_url="/food/dishes/%(containing_dish_id)s/"), name="amount_edit"),
    url(r'^dishes/(?P<pk>\d+)/delete/$', DeleteView.as_view( model=Dish, success_url="/food/dishes/"), name="dish_delete"),

    url(r'^meals/$', ListView.as_view( model=Meal ), name="meal_list"),
#    url(r'^meals/add/$', CreateView.as_view( model=Meal, success_url="/food/meals/%(id)s/" ), name="meal_add"),
    url(r'^meals/(?P<pk>\d+)/$', DetailView.as_view( model = Meal ), name="meal_detail"),
    url(r'^meals/(?P<pk>\d+)/edit/$', UpdateView.as_view( model=Meal, success_url="/food/meals/%(id)s/"), name="meal_edit"),
    url(r'^meals/(?P<meal_id>\d+)/edit/(?P<pk>\d+)/$', UpdateView.as_view( model=Eating, success_url="/food/meals/%(meal_id)s/"), name="eating_edit"),
    url(r'^meals/(?P<pk>\d+)/delete/$', DeleteView.as_view( model=Meal, success_url="/food/meals/"), name="meal_delete"),
)
