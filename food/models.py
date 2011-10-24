import datetime
import sys

from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.forms import ModelForm
from django.contrib.auth.models import User



UNIT_CHOICES = (
        ('g', 'grams'),
        ('ml', 'millilitres'),
        # units for stock pots, cups of tea, eggs, garlic cloves etc
        # think of a better name?
        ('items', 'items')
    )


class Comestible(models.Model):
    is_dish = models.BooleanField(default=True, editable=False)
    unit = models.CharField(max_length=5, choices=UNIT_CHOICES, default="g")

    def get_child(self):
        if self.is_dish:
            return self.dish
        else:
            return self.ingredient

    child = property(get_child)

    def __unicode__(self):
        return self.child.__unicode__()


class Ingredient(Comestible):
    name = models.CharField(max_length=200, unique=True)
    quantity = models.DecimalField(max_digits=8, decimal_places=2, default=100)
    calories = models.DecimalField(max_digits=8, decimal_places=2)

    def __unicode__(self):
        return self.name

    def get_comestible(self):
        return self.comestible_ptr

    comestible = property(get_comestible)

    def save(self, *args, **kwargs):
        # so that the related comestible knows this is an ingredient:
        self.is_dish = False
        # Call the "real" save() method.
        super(Ingredient, self).save(*args, **kwargs)

    class Meta:
        ordering = ['name']


class Dish(Comestible):
    name = models.CharField(max_length=200)
    # quantity has null=True because it doesn't use the default value when
    # entered blank, but it shouldn't be 0 for division reasons in calories
    # calculations
    # - add something to validation?
    # - or make both blank=False and null=False?
    quantity = models.DecimalField(max_digits=8, decimal_places=2, blank=True,
                                   default=500, null=True)
    date_cooked = models.DateField("Cooked on:", default=datetime.date.today)
    cooks = models.ManyToManyField(User, related_name='cooked_dishes')
    recipe_url = models.URLField("Link to the recipe for this dish", blank=True,
                                 null=True)
    calories = models.DecimalField(max_digits=8, decimal_places=2, null=True,
                                   editable=False)

    def __unicode__(self):
        return self.name+u" ("+unicode(self.date_cooked)+u")"

    def get_comestible(self):
        return self.comestible_ptr

    comestible = property(get_comestible)

# perhaps Dish also needs to update is_dish when saving, since defaults seem to
# be broken with South...

    def save(self, *args, **kwargs):
        # Calculate calories for the dish if it already exists
        # New dish needs to be saved again after amounts are created to
        # calculate calories
        if self.id: # (if this dish already exists)
            self.calories = sum(amount.calories for amount in
                                self.contained_comestibles_set.all())
        # Call the "real" save() method
        super(Dish, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "dishes"
        ordering = ['-date_cooked']


class DishForm(ModelForm):
    class Meta:
        model = Dish


class Amount(models.Model):
    containing_dish = models.ForeignKey(Dish,
        related_name='contained_comestibles_set') # shorten this, align better
    contained_comestible = models.ForeignKey(Comestible,
        related_name='containing_dishes_set') # shorten this, align better
    quantity = models.DecimalField(max_digits=8, decimal_places=2, blank=True,
                                   default=0, null=True)
    calories = models.DecimalField(max_digits=8, decimal_places=2, null=True,
                                   editable=False)

    def __unicode__(self):
        return unicode(self.contained_comestible)

    def save(self, *args, **kwargs):
        if (self.contained_comestible.is_dish and
            self.contained_comestible.dish == self.containing_dish):
            # This allows following amounts to be saved correctly,
            # but no notification to user...
            return u"A dish cannot contain itself"
            # This fails obviously, but following valid amounts aren't saved
#            raise Exception, u"A dish cannot contain itself"
        else:
            # Calculate calories for the dish
            self.calories = (self.quantity *
                             self.contained_comestible.child.calories /
                             self.contained_comestible.child.quantity)
            # Call the "real" save() method
            super(Amount, self).save(*args, **kwargs)

#    class Meta:
#        order_with_respect_to = 'containing_dish'


class Meal(models.Model):
    NAME_CHOICES = (
        ('breakfast', 'breakfast'),
        ('lunch', 'lunch'),
        ('dinner', 'dinner'),
        ('snack', 'snack'),
        ('elevenses', 'elevenses'),
        ('brunch', 'brunch'),
        ('second breakfast', 'second breakfast'),
        ('tea', 'tea'),
    )
    name = models.CharField(max_length=16, choices=NAME_CHOICES)
    date = models.DateField("On:", default=datetime.date.today)
    time = models.TimeField("at:")  # make defaults for each name choice...
    user = models.ForeignKey(User, related_name='meals')
    comestibles = models.ManyToManyField(Comestible, through='Portion',
                                         editable=False)
    calories = models.DecimalField(max_digits=8, decimal_places=2, null=True,
                                   editable=False)

    def __unicode__(self):
        return self.name+u" on "+unicode(self.date)

    def save(self, *args, **kwargs):
        # Calculate calories for the meal if it already has portions
        # New meal needs to be saved again after portions are created to
        # calculate calories
        if self.id: # (if this meal already exists)
           self.calories = sum(portion.calories for portion in
                               Portion.objects.filter(meal=self))
        # Call the "real" save() method
        super(Meal, self).save(*args, **kwargs)

    class Meta:
        ordering = ['date', 'time']


class MealForm(ModelForm):
    class Meta:
        model = Meal


class Eating(models.Model):
    comestible = models.ForeignKey(Comestible)
    meal = models.ForeignKey(Meal)
    quantity = models.DecimalField("the quantity eaten", max_digits=8,
                                   decimal_places=2, blank=True, default=0,
                                   null=True)
    calories = models.DecimalField(max_digits=8, decimal_places=2, null=True,
                                   editable=False)

    def __unicode__(self):
        return unicode(self.comestible)

    def save(self, *args, **kwargs):
        # Calculate calories for the eating
        self.calories = (self.quantity *
                         self.comestible.child.calories /
                         self.comestible.child.quantity)
        # Call the "real" save() method
        super(Eating, self).save(*args, **kwargs)

#    class Meta:
#        order_with_respect_to = 'meal'


class Portion(models.Model):
    comestible = models.ForeignKey(Comestible)
    meal = models.ForeignKey(Meal)
    quantity = models.DecimalField("the quantity eaten", max_digits=8,
                                   decimal_places=2, blank=True, default=0,
                                   null=True)
    calories = models.DecimalField(max_digits=8, decimal_places=2, null=True,
                                   editable=False)

    def __unicode__(self):
        return unicode(self.comestible)

    def save(self, *args, **kwargs):
        # Calculate calories for the portion
        self.calories = (self.quantity *
                         self.comestible.child.calories /
                         self.comestible.child.quantity)
        # Call the "real" save() method
        super(Portion, self).save(*args, **kwargs)

#    class Meta:
#        order_with_respect_to = 'meal'


# Signal receivers update related objects in order to recalculate their
# calories when something changes

############################ Eating ##################################

@receiver(post_save, sender=Ingredient)
def update_on_ingredient_save(sender, **kwargs):
    ingredient = kwargs['instance']
    print >> sys.stderr, "Instance: ingredient", ingredient
    for amount in Amount.objects.filter(contained_comestible__id=ingredient.id):
        print >> sys.stderr, ("Updating amount", amount, "in",
                              amount.containing_dish, amount.calories,
                              "calories")
        amount.save()
    for eating in Eating.objects.filter(comestible__id=ingredient.id):
        print >> sys.stderr, ("Updating eating", eating, "in", eating.meal,
                              eating.calories)
        eating.save()

# This is triggered for each amount when saving the formset
# Perhaps create a new signal for the formset to do it only once?
@receiver(post_save, sender=Amount)
def update_on_amount_save(sender, **kwargs):
    amount = kwargs['instance']
    dish = amount.containing_dish
    print >> sys.stderr, ("Instance: amount", amount, "; updating dish", dish,
                          dish.calories, "calories")
    dish.save()

@receiver(post_save, sender=Dish)
def update_on_dish_save(sender, **kwargs):
    dish = kwargs['instance']
    print >> sys.stderr, "Instance: dish", dish
    for amount in Amount.objects.filter(contained_comestible__id=dish.id):
        print >> sys.stderr, ("Updating amount", amount, "in",
                              amount.containing_dish, amount.calories,
                              "calories")
        amount.save()
    for eating in Eating.objects.filter(comestible__id=dish.id):
        print >> sys.stderr, ("Updating eating", eating, "in", eating.meal,
                              eating.calories)
        eating.save()

# This is triggered for each eating when saving the formset
# Perhaps create a new signal for the formset to do it only once?
@receiver(post_save, sender=Eating)
def update_on_eating_save(sender, **kwargs):
    eating = kwargs['instance']
    meal = eating.meal
    print >> sys.stderr, ("Instance: eating", eating, "; updating meal", meal,
                          meal.calories, "calories")
    meal.save()

# All ForeignKey and OneToOne fields have on_delete=CASCADE by default, so:
#     ingredient deleted --> comestible deleted --> amounts deleted (via contained_comestible FK)
#     dish deleted       --> comestible deleted --> amounts deleted (via contained_comestible FK or containing_dish FK)
#     ingredient deleted --> comestible deleted --> eatings deleted (via comestible FK)
#     dish deleted       --> comestible deleted --> eatings deleted (via comestible FK or meal FK)
# ... so we only need to deal here with amounts and eatings being deleted (both
# directly from the big formsets and after cascading).

@receiver(post_delete, sender=Amount)
def update_on_amount_delete(sender, **kwargs):
    amount = kwargs['instance']
    # amounts can be deleted as a cascading result of their containing
    # dish having been deleted, so a deleted amount won't always have a
    # containing dish to update
    try:
        dish = amount.containing_dish
        print >> sys.stderr, (
            "Instance deleted: amount (can't get name); updating containing_dish",
            dish, dish.calories, "calories"
        )
        dish.save()
    except Dish.DoesNotExist:
        print >> sys.stderr, (
            "Instance deleted: amount (can't get name); containing dish has already been deleted"
        )

@receiver(post_delete, sender=Eating)
def update_on_eating_delete(sender, **kwargs):
    eating = kwargs['instance']
    # eatings can be deleted as a cascading result of their meal having been
    # deleted, so a deleted eating won't always have a meal to update
    try:
        meal = eating.meal
        print >> sys.stderr, (
            "Instance deleted: eating (can't get name); updating meal", meal,
            meal.calories, "calories"
        )
        meal.save()
    except Meal.DoesNotExist:
        print >> sys.stderr, (
            "Instance deleted: eating (can't get name); meal has already been deleted"
        )

############################ Portion ##################################

@receiver(post_save, sender=Ingredient)
def update_on_ingredient_save(sender, **kwargs):
    ingredient = kwargs['instance']
    print >> sys.stderr, "Instance: ingredient", ingredient
    for amount in Amount.objects.filter(contained_comestible__id=ingredient.id):
        print >> sys.stderr, ("Updating amount", amount, "in",
                              amount.containing_dish, amount.calories,
                              "calories")
        amount.save()
    for portion in Portion.objects.filter(comestible__id=ingredient.id):
        print >> sys.stderr, ("Updating portion", portion, "in", portion.meal,
                              portion.calories)
        portion.save()

# This is triggered for each amount when saving the formset
# Perhaps create a new signal for the formset to do it only once?
@receiver(post_save, sender=Amount)
def update_on_amount_save(sender, **kwargs):
    amount = kwargs['instance']
    dish = amount.containing_dish
    print >> sys.stderr, ("Instance: amount", amount, "; updating dish", dish,
                          dish.calories, "calories")
    dish.save()

@receiver(post_save, sender=Dish)
def update_on_dish_save(sender, **kwargs):
    dish = kwargs['instance']
    print >> sys.stderr, "Instance: dish", dish
    for amount in Amount.objects.filter(contained_comestible__id=dish.id):
        print >> sys.stderr, ("Updating amount", amount, "in",
                              amount.containing_dish, amount.calories,
                              "calories")
        amount.save()
    for portion in Portion.objects.filter(comestible__id=dish.id):
        print >> sys.stderr, ("Updating portion", portion, "in", portion.meal,
                              portion.calories)
        portion.save()

# This is triggered for each portion when saving the formset
# Perhaps create a new signal for the formset to do it only once?
@receiver(post_save, sender=Portion)
def update_on_portion_save(sender, **kwargs):
    portion = kwargs['instance']
    meal = portion.meal
    print >> sys.stderr, ("Instance: portion", portion, "; updating meal", meal,
                          meal.calories, "calories")
    meal.save()

# All ForeignKey and OneToOne fields have on_delete=CASCADE by default, so:
#     ingredient deleted --> comestible deleted --> amounts deleted (via contained_comestible FK)
#     dish deleted       --> comestible deleted --> amounts deleted (via contained_comestible FK or containing_dish FK)
#     ingredient deleted --> comestible deleted --> portions deleted (via comestible FK)
#     dish deleted       --> comestible deleted --> portions deleted (via comestible FK or meal FK)
# ... so we only need to deal here with amounts and portions being deleted (both
# directly from the big formsets and after cascading).

@receiver(post_delete, sender=Amount)
def update_on_amount_delete(sender, **kwargs):
    amount = kwargs['instance']
    # amounts can be deleted as a cascading result of their containing
    # dish having been deleted, so a deleted amount won't always have a
    # containing dish to update
    try:
        dish = amount.containing_dish
        print >> sys.stderr, (
            "Instance deleted: amount (can't get name); updating containing_dish",
            dish, dish.calories, "calories"
        )
        dish.save()
    except Dish.DoesNotExist:
        print >> sys.stderr, (
            "Instance deleted: amount (can't get name); containing dish has already been deleted"
        )

@receiver(post_delete, sender=Portion)
def update_on_portion_delete(sender, **kwargs):
    portion = kwargs['instance']
    # portions can be deleted as a cascading result of their meal having been
    # deleted, so a deleted portion won't always have a meal to update
    try:
        meal = portion.meal
        print >> sys.stderr, (
            "Instance deleted: portion (can't get name); updating meal", meal,
            meal.calories, "calories"
        )
        meal.save()
    except Meal.DoesNotExist:
        print >> sys.stderr, (
            "Instance deleted: portion (can't get name); meal has already been deleted"
        )


#################################

#### from Comestible:
#    CHILD_MODEL_CHOICES = (
#        ('Ingredient', 'Ingredient'),
#        ('Dish', 'Dish'),
#    )
#    child_model = models.CharField(max_length=10, choices=CHILD_MODEL_CHOICES,
#                                   editable=False, default='Dish')
#### from Ingredient.save():
#        # so that the related comestible knows this is an ingredient
#        self.child_model = 'Ingredient'


##### move clagginess into a ratings app later
##    CLAGGINESS_CHOICES = (
##        ('A', 'anti-clag'),
##        ('B', 'balanced'), # better name? bitclag?
##        ('C', 'clag')
##    )
##    # totes subjective opinion :)
##    clagginess = models.CharField(max_length=1, choices=CLAGGINESS_CHOICES,
##                                  blank=True)

