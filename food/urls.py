from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('food.views',
    # Example:
    # (r'^everydayeating/', include('everydayeating.foo.urls')),
    (r'^ingredients/$', 'ingredient_index'),
    (r'^ingredients/(?P<ingredient_id>\d+)/$', 'ingredient_detail'),
    (r'^ingredients/add/$', 'ingredient_add'),
)