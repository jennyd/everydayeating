from django.conf.urls.defaults import *
# from food.views import 
from django.views.generic import TemplateView, ListView, CreateView, DetailView, UpdateView, DeleteView
from food.models import Ingredient, Dish, Amount

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('food.views',
    # Example:
    # (r'^everydayeating/', include('everydayeating.foo.urls')),
)

urlpatterns += patterns('',
    url(r'^$', TemplateView.as_view(template_name='food/food_index.html'), name="food_index"),
    url(r'^ingredients/$', ListView.as_view( queryset=Ingredient.objects.all().order_by("name") ), name="ingredient_list"),
    url(r'^ingredients/add/$', CreateView.as_view( model=Ingredient, success_url="/food/ingredients/" ), name="ingredient_add"),
    url(r'^ingredients/(?P<pk>\d+)/$', DetailView.as_view( model=Ingredient ), name="ingredient_detail"),
    url(r'^ingredients/(?P<pk>\d+)/edit/$', UpdateView.as_view( model=Ingredient, success_url="/food/ingredients/"), name="ingredient_edit"),
    url(r'^ingredients/(?P<pk>\d+)/delete/$', DeleteView.as_view( model=Ingredient, success_url="/food/ingredients/"), name="ingredient_delete"),
    url(r'^dishes/$', ListView.as_view( queryset=Dish.objects.all().order_by("-date_cooked") ), name="dish_list"),
    url(r'^dishes/(?P<pk>\d+)/$', DetailView.as_view( model = Dish ), name="dish_detail"),
    url(r'^dishes/(?P<pk>\d+)/edit/$', UpdateView.as_view( model=Dish, success_url="/food/dishes/%(id)s/"), name="dish_edit"),
    url(r'^dishes/(?P<dish_id>\d+)/edit/(?P<pk>\d+)/$', UpdateView.as_view( model=Amount, success_url="/food/dishes/%(containing_dish_id)s/"), name="amount_edit"),
)
