from django.db import models

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

