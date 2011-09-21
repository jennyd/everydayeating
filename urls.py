from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^food/ingredients/$', 'food.views.ingredient_index'),
    (r'^food/ingredients/(?P<ingredient_id>\d+)/$', 'food.views.ingredient_detail'),
    (r'^food/ingredients/add/$', 'food.views.ingredient_add'),
    
    # Example:
    # (r'^everydayeating/', include('everydayeating.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
)
