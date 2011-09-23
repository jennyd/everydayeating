from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('food.views',
    # Example:
    # (r'^everydayeating/', include('everydayeating.foo.urls')),
    (r'^ingredients/$', 'ingredient_index'),
    (r'^ingredients/(?P<ingredient_id>\d+)/$', 'ingredient_detail'),
    (r'^ingredients/(?P<ingredient_id>\d+)/edit/$', 'ingredient_edit'),
    (r'^ingredients/(?P<ingredient_id>\d+)/edit/thanks/$', 'ingredient_edit_thanks'),
    (r'^ingredients/add/$', 'ingredient_add'),
    (r'^ingredients/add/thanks/$', 'ingredient_add_thanks'),
    (r'^dishes/$', 'dish_index'),
    (r'^dish/(?P<dish_id>\d+)/$', 'dish_detail'),
    (r'^dishes/(?P<dish_id>\d+)/edit/$', 'dish_edit'),
    (r'^dishes/(?P<dish_id>\d+)/edit/thanks/$', 'dish_edit_thanks'),
)
