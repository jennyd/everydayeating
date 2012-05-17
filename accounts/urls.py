from django.conf.urls.defaults import *

from accounts.views import ProfileDetailView

from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    url(r'^(?P<username>[\w@+.-]+)/profile/$', ProfileDetailView.as_view(), name="profile_detail"),
)
