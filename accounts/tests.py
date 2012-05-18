from django.core.urlresolvers import reverse
from django.test import TestCase

from django.contrib.auth.models import User

from accounts.models import Household, Profile


fake_pk = 9999999999

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


class RegistrationTestCase(TestCase):
    def test_register(self):
        response = self.client.get(reverse("registration_register"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.templates), 2)
        self.assertTemplateUsed(response, "registration/registration_form.html")
        self.assertTemplateUsed(response, "food/base.html")
        # Not sure if it's necessary to check these - they are provided by
        # django.contrib.auth.views.login
        self.assertTrue("csrf_token" in response.context)
        self.assertTrue("form" in response.context)
        # user is AnonymousUser here:
        self.assertFalse(response.context["user"].is_authenticated())

        response = self.client.post(reverse("registration_register"),
                                    data={"username": "jenny",
                                          "email": "jenny@example.com",
                                          "password1": "right",
                                          "password2": "right"},
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.templates), 2)
        self.assertTemplateUsed(response, "registration/registration_complete.html")
        self.assertTemplateUsed(response, "food/base.html")
        self.assertTrue(User.objects.get(username="jenny"))
        self.assertTrue(Household.objects.get(name="jenny's household"))
        self.assertTrue(Profile.objects.get(user__username="jenny"))


class AccountsViewsTestCase(TestCase):
    def test_household_detail(self):
        # Create a user (household and profile created by signal receiver):
        user = User.objects.create_user("jenny", "a@b.com", "password")

        with self.assertNumQueries(4):
            response = self.client.get(reverse("household_detail",
                                           kwargs={'pk': user.profile.household.id}),)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.templates), 2)
        self.assertTemplateUsed(response, "accounts/household_detail.html")
        self.assertTemplateUsed(response, "food/base.html")
        self.assertTrue("household" in response.context)
        # admin should be here already via select_related():
        with self.assertNumQueries(0):
            print "admin:", response.context['household'].admin
        self.assertTrue("members" in response.context)


