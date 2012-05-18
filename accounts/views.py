from django.shortcuts import get_object_or_404
from django.views.generic import DetailView

from django.contrib.auth.models import User

from accounts.models import Profile, Household


class ProfileDetailView(DetailView):

    queryset = Profile.objects.select_related('user', 'household').all()

    def get_object(self):
        user = get_object_or_404(User, username=self.kwargs['username'])

        # Just use this instead of the following two lines?
        # object = user.profile

        self.kwargs['pk'] = user.profile.id
        object = super(ProfileDetailView, self).get_object()

        # Return the object
        return object


class HouseholdDetailView(DetailView):

    # select_related just adds the household's admin user here:
    queryset = Household.objects.select_related().all()

    def get_context_data(self, **kwargs):

        # Call the base implementation first to get a context
        context = super(HouseholdDetailView, self).get_context_data(**kwargs)

        # Add in household members
        members = User.objects.filter(profile__household__id=self.kwargs['pk'])

        context.update({
            'members': members,
        })
        return context

