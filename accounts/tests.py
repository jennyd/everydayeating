from django.test import TestCase

from django.contrib.auth.models import User

from accounts.models import Household, Profile


class SignalTestCase(TestCase):
    def test_create_household_and_profile_on_create_user(self):
        """
        Tests that a household and profile are created for a new user.
        """
        # Create a new user:
        user = User.objects.create_user("jenny", "a@b.com", "password")

        # A new household and a profile should have been created for the user:
        self.assertTrue(Household.objects.get(admin=user, name="jenny's household"))
        self.assertTrue(Profile.objects.get(user=user))

