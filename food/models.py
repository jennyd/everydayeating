from django.db import models
from django.forms import ModelForm


UNIT_CHOICES = (
        ('g', 'grams'),
        ('ml', 'millilitres'),
        ('items', 'items') # units for stock pots, tea with milk, eggs, garlic cloves etc - better name?
    )


class Comestible(models.Model):
    CHILD_MODEL_CHOICES = (
        ('Ingredient', 'Ingredient'),
        ('Dish', 'Dish'),
    )
    child_model = models.CharField(max_length=10, choices=CHILD_MODEL_CHOICES, editable=False, default='Dish')
    is_dish = models.BooleanField(default=True, editable=False) # as alternative to child_model
    unit = models.CharField(max_length=5, choices=UNIT_CHOICES, default="g")

    def get_child(self):
        if self.is_dish == True:
            return self.dish
        else:
            return self.ingredient

    child = property(get_child)

    def __unicode__(self):
        return self.child.name+u" ("+self.child_model+u")"


class Ingredient(Comestible):
    name = models.CharField(max_length=200, unique=True)
    quantity = models.DecimalField(max_digits=8, decimal_places=2, default=100)
    calories = models.DecimalField(max_digits=8, decimal_places=2)
    # add other nutrients to track later: fat, calories from carbs etc

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.child_model = 'Ingredient' # so that the related comestible knows this is an ingredient
        self.is_dish = False # as alternative to child_model
        super(Ingredient, self).save(*args, **kwargs) # Call the "real" save() method.

    class Meta:
        ordering = ['name']


class Dish(Comestible):
    name = models.CharField(max_length=200)
    quantity = models.DecimalField(max_digits=8, decimal_places=2, blank=True, default=500, null=True)
    date_cooked = models.DateField("the date on which the dish is cooked") # default...

    def __unicode__(self):
        return self.name

    def get_dish_calories(self):
        return sum(amount.calories for amount in self.contained_comestibles_set.all())

    calories = property(get_dish_calories)

# perhaps Dish also needs a custom save method for child_model/is_dish, since defaults seem to be broken with South...

    class Meta:
        verbose_name_plural = "dishes"
        ordering = ['-date_cooked']


class Amount(models.Model):
    containing_dish = models.ForeignKey(Dish, related_name='contained_comestibles_set')
    contained_comestible = models.ForeignKey(Comestible, related_name='containing_dishes_set')
    quantity = models.DecimalField("the quantity of this ingredient in the dish, in ingredient units", max_digits=8, decimal_places=2, blank=True, default=0, null=True)

    def __unicode__(self):
        return unicode(self.contained_comestible)

    def get_amount_calories(self):
        return self.quantity * self.contained_comestible.child.calories / self.contained_comestible.child.quantity

    calories = property(get_amount_calories)

    def save(self, *args, **kwargs):
        if self.contained_comestible.is_dish == True and self.contained_comestible.dish == self.containing_dish:
            return u"A dish cannot contain itself" # allows following amounts to be saved correctly, but no notification to user...
#            raise Exception, u"A dish cannot contain itself" # fails obviously, but following allowable amounts aren't saved
        else:
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
    date = models.DateField("the date on which the meal is eaten")
    time = models.TimeField("the time at which the meal is eaten")  # make defaults for each name choice...
    comestibles = models.ManyToManyField(Comestible, through='Eating', editable=False)

    def __unicode__(self):
        return self.name+u" on "+unicode(self.date)

    def get_meal_calories(self):
        return sum(eating.calories for eating in Eating.objects.filter(meal=self))

    calories = property(get_meal_calories)

    class Meta:
        ordering = ['date', 'time']


class Eating(models.Model):
    comestible = models.ForeignKey(Comestible)
    meal = models.ForeignKey(Meal)
    quantity = models.DecimalField("the quantity eaten", max_digits=8, decimal_places=2, blank=True, default=0, null=True)

    def __unicode__(self):
        return unicode(self.comestible)

    def get_eating_calories(self):
        return self.quantity * self.comestible.child.calories / self.comestible.child.quantity

    calories = property(get_eating_calories)

#    class Meta:
#        order_with_respect_to = 'meal'


#################################

#class DishForm(ModelForm):
#    class Meta: 
#        model = Dish


##### move clagginess into a ratings app later
##    CLAGGINESS_CHOICES = (
##        ('A', 'anti-clag'),
##        ('B', 'balanced'), # better name? bitclag?
##        ('C', 'clag')
##    )
##    clagginess = models.CharField(max_length=1, choices=CLAGGINESS_CHOICES, blank=True) # totes subjective opinion :)

