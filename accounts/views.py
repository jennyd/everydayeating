from django.shortcuts import get_object_or_404
from django.views.generic import DetailView

from django.contrib.auth.models import User

from accounts.models import Profile, Household


class ProfileDetailView(DetailView):

    model = Profile

    def get_object(self):
        user = get_object_or_404(User, username=self.kwargs['username'])

        # Just use this instead of the following two lines?
        # object = user.profile

        self.kwargs['pk'] = user.profile.id
        object = super(ProfileDetailView, self).get_object()

        # Return the object
        return object

