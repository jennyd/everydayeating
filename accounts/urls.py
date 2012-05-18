from django.conf.urls.defaults import *

from accounts.views import ProfileDetailView, HouseholdDetailView

from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    url(r'^user/(?P<username>[\w@+.-]+)/profile/$', ProfileDetailView.as_view(), name="profile_detail"),
    url(r'^household/(?P<pk>\d+)/$', HouseholdDetailView.as_view(), name="household_detail"),
)
