import datetime, sys
from django.db import models
from django.forms import ModelForm
from django.db.models.signals import post_save
from django.dispatch import receiver



UNIT_CHOICES = (
        ('g', 'grams'),
        ('ml', 'millilitres'),
        ('items', 'items') # units for stock pots, tea with milk, eggs, garlic cloves etc - better name?
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
        return self.child.__unicode__() # +u" ("+unicode(self.child.__class__)+u")"


class Ingredient(Comestible):
    name = models.CharField(max_length=200, unique=True)
    quantity = models.DecimalField(max_digits=8, decimal_places=2, default=100)
    calories = models.DecimalField(max_digits=8, decimal_places=2)
    # add other nutrients to track later: fat, calories from carbs etc

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.is_dish = False # so that the related comestible knows this is an ingredient (default=True)
        super(Ingredient, self).save(*args, **kwargs) # Call the "real" save() method.

    class Meta:
        ordering = ['name']


class Dish(Comestible):
    name = models.CharField(max_length=200)
    # quantity has null=True because it doesn't use the default value when entered blank
    # but it shouldn't be 0 for division reasons in calories calculations
    # add something to validation?
    # or make both blank=False and null=False?
    quantity = models.DecimalField(max_digits=8, decimal_places=2, blank=True, default=500, null=True)
    date_cooked = models.DateField("Cooked on:", default=datetime.date.today) # default...
    calories = models.DecimalField(max_digits=8, decimal_places=2, null=True, editable=False)

    def __unicode__(self):
        return self.name+u" ("+unicode(self.date_cooked)+u")"

# perhaps Dish also needs to update is_dish when saving, since defaults seem to be broken with South...

    def save(self, *args, **kwargs):
        # Calculate calories for the dish if it already exists
        # New dish needs to be saved again after amounts are created to calculate calories
        if self.id: # if this dish already exists
            self.calories = sum(amount.calories for amount in self.contained_comestibles_set.all())
        # Call the "real" save() method.
        super(Dish, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "dishes"
        ordering = ['-date_cooked']


class DishForm(ModelForm):
    class Meta:
        model = Dish


class Amount(models.Model):
    containing_dish = models.ForeignKey(Dish, related_name='contained_comestibles_set')
    contained_comestible = models.ForeignKey(Comestible, related_name='containing_dishes_set')
    quantity = models.DecimalField(max_digits=8, decimal_places=2, blank=True, default=0, null=True)
    calories = models.DecimalField(max_digits=8, decimal_places=2, null=True, editable=False)

    def __unicode__(self):
        return unicode(self.contained_comestible)

    def save(self, *args, **kwargs):
        if self.contained_comestible.is_dish and self.contained_comestible.dish == self.containing_dish:
            return u"A dish cannot contain itself" # allows following amounts to be saved correctly, but no notification to user...
#            raise Exception, u"A dish cannot contain itself" # fails obviously, but following allowable amounts aren't saved
        else:
            # Calculate calories for the dish
            self.calories = self.quantity * self.contained_comestible.child.calories / self.contained_comestible.child.quantity
            super(Amount, self).save(*args, **kwargs) # Call the "real" save() method.

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
    comestibles = models.ManyToManyField(Comestible, through='Eating', editable=False)
    calories = models.DecimalField(max_digits=8, decimal_places=2, null=True, editable=False)

    def __unicode__(self):
        return self.name+u" on "+unicode(self.date)

    def save(self, *args, **kwargs):
        # Calculate calories for the meal if it already has eatings
        # New meal needs to be saved again after eatings are created to calculate calories
        if self.id: # if this meal already exists
           self.calories = sum(eating.calories for eating in Eating.objects.filter(meal=self))
        # Call the "real" save() method.
        super(Meal, self).save(*args, **kwargs)

    class Meta:
        ordering = ['date', 'time']


class MealForm(ModelForm):
    class Meta:
        model = Meal


class Eating(models.Model):
    comestible = models.ForeignKey(Comestible)
    meal = models.ForeignKey(Meal)
    quantity = models.DecimalField("the quantity eaten", max_digits=8, decimal_places=2, blank=True, default=0, null=True)
    calories = models.DecimalField(max_digits=8, decimal_places=2, null=True, editable=False)

    def __unicode__(self):
        return unicode(self.comestible)

    def save(self, *args, **kwargs):
        # Calculate calories for the eating
        self.calories = self.quantity * self.comestible.child.calories / self.comestible.child.quantity
        # Call the "real" save() method.
        super(Eating, self).save(*args, **kwargs)

#    class Meta:
#        order_with_respect_to = 'meal'


@receiver(post_save, sender=Ingredient)
def update_on_ingredient_save(sender, **kwargs):
    ingredient = kwargs['instance']
#    print >> sys.stderr, "Instance: ingredient", ingredient
    for amount in Amount.objects.filter(contained_comestible__id=ingredient.id):
#        print >> sys.stderr, "Updating amount", amount, "in", amount.containing_dish, amount.calories
        amount.save()
    for eating in Eating.objects.filter(comestible__id=ingredient.id):
#        print >> sys.stderr, "Updating eating", eating, "in", eating.meal, eating.calories
        eating.save()


#################################

#### from Comestible:
#    CHILD_MODEL_CHOICES = (
#        ('Ingredient', 'Ingredient'),
#        ('Dish', 'Dish'),
#    )
#    child_model = models.CharField(max_length=10, choices=CHILD_MODEL_CHOICES, editable=False, default='Dish')
#### from Ingredient.save():
#        self.child_model = 'Ingredient' # so that the related comestible knows this is an ingredient


##### move clagginess into a ratings app later
##    CLAGGINESS_CHOICES = (
##        ('A', 'anti-clag'),
##        ('B', 'balanced'), # better name? bitclag?
##        ('C', 'clag')
##    )
##    clagginess = models.CharField(max_length=1, choices=CLAGGINESS_CHOICES, blank=True) # totes subjective opinion :)

