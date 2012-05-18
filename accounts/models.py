import sys

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from django.contrib.auth.models import User


class Household(models.Model):
    # Should name be unique? Perhaps for publishing recipes...
    name = models.CharField(max_length=200)
    admin = models.ForeignKey(User, related_name='admin_for_set')
    is_active = models.BooleanField(default=True)

    def __unicode__(self):
        return self.name


class Profile(models.Model):
    # We don't need related_name here - user.profile returns a single object anyway:
    user = models.OneToOneField(User)
    # This is the current household of the user:
    household = models.ForeignKey(Household, related_name='user_profiles')
    display_name = models.CharField(max_length=80)

    def __unicode__(self):
        return self.display_name+u"'s profile"



@receiver(post_save, sender=User)
def create_household_and_profile_on_create_user(sender, **kwargs):
    if kwargs['created']: # if the user has just been created:
        user = kwargs['instance']
        print >> sys.stderr, "New user created:", user
        household = Household.objects.create(name=user.username+u"'s household",
                                             admin=user,
                                             )
        profile = Profile.objects.create(user=user,
                                         household=household,
                                         display_name=user.username
                                         )

