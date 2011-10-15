from django.conf.urls.defaults import *
from food.views import ingredient_manage, dish_amounts_form, meal_eating_form, MealWeekArchiveView, MealDayArchiveView
from django.views.generic import TemplateView, ListView, CreateView, DetailView, UpdateView, DeleteView, ArchiveIndexView, YearArchiveView, MonthArchiveView, WeekArchiveView, DayArchiveView
from food.models import Ingredient, Dish, Amount, Meal, Eating

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('food.views',
    url(r'^ingredients/manage/$', "ingredient_manage", name="ingredient_manage"),

    url(r'^dishes/add/$', "dish_amounts_form", name="dish_add"),
    url(r'^dishes/(?P<dish_id>\d+)/edit/$', "dish_amounts_form", name="dish_edit"),

    url(r'^meals/add/$', "meal_eating_form", name="meal_add"),
    url(r'^meals/(?P<meal_id>\d+)/edit/$', "meal_eating_form", name="meal_edit"),
)

urlpatterns += patterns('',
    url(r'^$', TemplateView.as_view( template_name='food/food_index.html' ), name="food_index"),

    url(r'^ingredients/$', ListView.as_view( model=Ingredient ), name="ingredient_list"),
    url(r'^ingredients/add/$', CreateView.as_view( model=Ingredient, success_url="/food/ingredients/" ), name="ingredient_add"),
    url(r'^ingredients/(?P<pk>\d+)/$', DetailView.as_view( model=Ingredient ), name="ingredient_detail"),
    url(r'^ingredients/(?P<pk>\d+)/edit/$', UpdateView.as_view( model=Ingredient, success_url="/food/ingredients/"), name="ingredient_edit"),
    url(r'^ingredients/(?P<pk>\d+)/delete/$', DeleteView.as_view( model=Ingredient, success_url="/food/ingredients/"), name="ingredient_delete"),

    url(r'^dishes/$', ListView.as_view( model=Dish ), name="dish_list"),
    url(r'^dishes/(?P<pk>\d+)/$', DetailView.as_view( model = Dish ), name="dish_detail"),
    url(r'^dishes/(?P<pk>\d+)/delete/$', DeleteView.as_view( model=Dish, success_url="/food/dishes/"), name="dish_delete"),

    url(r'^meals/$', ArchiveIndexView.as_view( model=Meal, date_field="date", allow_future=True ), name="meal_archive"),
    url(r'^meals/(?P<year>\d{4})/$', YearArchiveView.as_view( model=Meal, date_field="date", allow_future=True, make_object_list=True ), name="meal_archive_year"),
    url(r'^meals/(?P<year>\d{4})/(?P<month>\d{2})/$', MonthArchiveView.as_view( model=Meal, date_field="date", allow_future=True, month_format='%m' ), name="meal_archive_month"),
    url(r'^meals/(?P<year>\d{4})/week(?P<week>\d{2})/$', MealWeekArchiveView.as_view(), name="meal_archive_week"),
    url(r'^meals/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$', MealDayArchiveView.as_view(), name="meal_archive_day"),
    url(r'^meals/all/$', ListView.as_view( model=Meal ), name="meal_list"),
    url(r'^meals/(?P<pk>\d+)/$', DetailView.as_view( model = Meal ), name="meal_detail"),
    url(r'^meals/(?P<pk>\d+)/delete/$', DeleteView.as_view( model=Meal, success_url="/food/meals/"), name="meal_delete"),
)
