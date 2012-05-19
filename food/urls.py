from django.conf.urls.defaults import *
from django.contrib.auth.views import login, logout
from django.views.generic import TemplateView, ListView, CreateView, DetailView, UpdateView, DeleteView, ArchiveIndexView, YearArchiveView

from food.views import IngredientListView, IngredientCreateView, IngredientDetailView, IngredientUpdateView, IngredientDeleteView, ingredient_manage, DishListView, DishDetailView, dish_amounts_form, meal_portions_form, dish_multiply, dish_duplicate, meal_duplicate, MealMonthArchiveView, MealWeekArchiveView, MealDayArchiveView
from food.models import Ingredient, Dish, Amount, Meal, Portion

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('food.views',
    url(r'^ingredients/$', IngredientListView.as_view(), name="ingredient_list"),
    url(r'^ingredients/add/$', IngredientCreateView.as_view(), name="ingredient_add"),
    url(r'^ingredients/(?P<pk>\d+)/$', IngredientDetailView.as_view(), name="ingredient_detail"),
    url(r'^ingredients/(?P<pk>\d+)/edit/$', IngredientUpdateView.as_view(), name="ingredient_edit"),
    url(r'^ingredients/(?P<pk>\d+)/delete/$', IngredientDeleteView.as_view(), name="ingredient_delete"),
    url(r'^ingredients/manage/$', "ingredient_manage", name="ingredient_manage"),

    url(r'^dishes/$', DishListView.as_view(), name="dish_list"),
    url(r'^dishes/add/$', "dish_amounts_form", name="dish_add"),
    url(r'^dishes/(?P<pk>\d+)/$', DishDetailView.as_view(), name="dish_detail"),
    url(r'^dishes/(?P<dish_id>\d+)/edit/$', "dish_amounts_form", name="dish_edit"),
    url(r'^dishes/(?P<dish_id>\d+)/multiply/$', "dish_multiply", name="dish_multiply"),
    url(r'^dishes/(?P<dish_id>\d+)/duplicate/$', "dish_duplicate", name="dish_duplicate"),

    url(r'^meals/add/$', "meal_portions_form", name="meal_add"),
    url(r'^meals/(?P<meal_id>\d+)/edit/$', "meal_portions_form", name="meal_edit"),
    url(r'^meals/(?P<meal_id>\d+)/duplicate/$', "meal_duplicate", name="meal_duplicate"),
)

urlpatterns += patterns('',
    url(r'^$', TemplateView.as_view( template_name='food/food_index.html' ), name="food_index"),
    url(r'^login/$', 'django.contrib.auth.views.login', { 'template_name': 'food/login.html' }, name="login"),
    url(r'^logout/$', 'django.contrib.auth.views.logout', { 'next_page': '/food/' }, name="logout"),

    url(r'^dishes/(?P<pk>\d+)/delete/$', DeleteView.as_view( model=Dish, success_url="/food/dishes/"), name="dish_delete"),

    url(r'^meals/$', ArchiveIndexView.as_view( model=Meal, date_field="date", allow_future=True ), name="meal_archive"),
    url(r'^meals/(?P<year>\d{4})/$', YearArchiveView.as_view( model=Meal, date_field="date", allow_future=True, make_object_list=True ), name="meal_archive_year"),
    url(r'^meals/(?P<year>\d{4})/(?P<month>\d{2})/$', MealMonthArchiveView.as_view(), name="meal_archive_month"),
    url(r'^meals/(?P<year>\d{4})/week(?P<week>\d{1,2})/$', MealWeekArchiveView.as_view(), name="meal_archive_week"),
    url(r'^meals/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$', MealDayArchiveView.as_view(), name="meal_archive_day"),
    url(r'^meals/all/$', ListView.as_view( model=Meal ), name="meal_list"),
    url(r'^meals/(?P<pk>\d+)/$', DetailView.as_view( model = Meal ), name="meal_detail"),
    url(r'^meals/(?P<pk>\d+)/delete/$', DeleteView.as_view( model=Meal, success_url="/food/meals/"), name="meal_delete"),
)
