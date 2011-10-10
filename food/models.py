from django.db import models
from django.forms import ModelForm


UNIT_CHOICES = (
        ('g', 'grams'),
        ('ml', 'millilitres'),
        ('items', 'items') # units for stock pots, tea with milk, eggs, garlic cloves etc - better name?
    )


class Comestible(models.Model):
    CHILD_MODEL_CHOICES = (
        ('I', 'Ingredient'),
        ('D', 'Dish'),
    )
    child_model = models.CharField(max_length=1, choices=CHILD_MODEL_CHOICES, editable=False, default='D')
    is_dish = models.BooleanField(default=True, editable=False) # as alternative to child_model
    dishy = models.BooleanField(default=True, editable=False) # as alternative to child_model
    unit = models.CharField(max_length=5, choices=UNIT_CHOICES, default="g")

#    def is_dish(self):
#        if self.dishy == True:
#            return True
#        elif self.dishy == False:
#            return False
#        else:
#            raise Exception, u"Comestible.is_dish() is somehow rubbish"

#    def is_dish(self):
#        if self.child_model == 'D':
#            return True
#        elif self.child_model == 'I':
#            return False
#        else:
#            raise Exception, u"Child model field is useless in Comestible.is_dish()"

    def __unicode__(self):
        if self.is_dish == True:
            return u"Dish: "+self.dish.name
        else:
            return u"Ingredient: "+self.ingredient.name
#        elif self.is_dish() == False:
#            return u"Ingredient: "+self.ingredient.name
#        else:
#            raise Exception, u"Comestible.__unicode__() is broken"

    def child_quantity(self):
        if self.is_dish == True:
            return self.dish.total_quantity
        else:
            return self.ingredient.reference_quantity

    def child_calories(self):
        if self.is_dish == True:
            return self.dish.get_dish_calories()
        else:
            return self.ingredient.calories


class Ingredient(Comestible):
    name = models.CharField(max_length=200, unique=True)
    reference_quantity = models.DecimalField("the quantity to which the calorie value refers", max_digits=8, decimal_places=2, default=100)
    quantity = models.DecimalField(max_digits=8, decimal_places=2, default=100) # not being used yet
    calories = models.DecimalField(max_digits=8, decimal_places=2)
    # add other nutrients to track later? fat, calories from carbs etc

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.child_model = 'I' # so that the related comestible knows this is an ingredient
        self.is_dish = False # as alternative to child_model
        self.dishy = False # as alternative to child_model
        super(Ingredient, self).save(*args, **kwargs) # Call the "real" save() method.


class Dish(Comestible):
    name = models.CharField(max_length=200)
    total_quantity = models.DecimalField("the total quantity of the finished dish", max_digits=8, decimal_places=2, blank=True, default=500, null=True)
    quantity = models.DecimalField(max_digits=8, decimal_places=2, blank=True, default=500, null=True) # not being used yet
    date_cooked = models.DateField("the date on which the dish is cooked") # default...

    def __unicode__(self):
        return self.name

    def get_dish_calories(self):
        return sum(amount.calories for amount in self.contained_comestibles_set.all())

    calories = property(get_dish_calories)

# perhaps Dish also needs a custom save method for child_model/is_dish/dishy, since defaults seem to be broken with South...

    class Meta:
        verbose_name_plural = "dishes"


class Amount(models.Model):
    containing_dish = models.ForeignKey(Dish, related_name='contained_comestibles_set')
    contained_comestible = models.ForeignKey(Comestible, related_name='containing_dishes_set')
    quantity = models.DecimalField("the quantity of this ingredient in the dish, in ingredient units", max_digits=8, decimal_places=2, blank=True, default=0, null=True)

    def __unicode__(self):
        return unicode(self.contained_comestible)

    def get_amount_calories(self):
        return self.quantity * self.contained_comestible.child_calories() / self.contained_comestible.child_quantity()

    calories = property(get_amount_calories)

#    def get_amount_calories(self):
#        try:
#            calories = self.contained_comestible.ingredient.calories
#            ref_quantity = self.contained_comestible.ingredient.reference_quantity
#        except Ingredient.DoesNotExist:
#            try:
#                calories = self.contained_comestible.dish.get_dish_calories()
#                ref_quantity = self.contained_comestible.dish.total_quantity
#            except Dish.DoesNotExist:
#                raise Comestible.DoesNotExist, "This is an amount of nothingness"
#        amount_calories = self.quantity * calories / ref_quantity
#        return amount_calories

    def save(self, *args, **kwargs):
        if self.contained_comestible.is_dish == True and self.contained_comestible.dish == self.containing_dish:
            return u"A dish cannot contain itself" # allows following amounts to be saved correctly, but no notification to user...
#            raise Exception, u"A dish cannot contain itself" # fails obviously, but following allowable amounts aren't saved
        else:
            super(Amount, self).save(*args, **kwargs) # Call the "real" save() method.


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


class Eating(models.Model):
    comestible = models.ForeignKey(Comestible)
    meal = models.ForeignKey(Meal)
    quantity = models.DecimalField("the quantity eaten", max_digits=8, decimal_places=2, blank=True, default=0, null=True)

    def __unicode__(self):
        return unicode(self.comestible)

    def get_eating_calories(self):
        return self.quantity * self.comestible.child_calories() / self.comestible.child_quantity()

    calories = property(get_eating_calories)

#    def get_eating_calories(self):
#        if self.comestible.child_model == 'I':
#            calories = self.comestible.ingredient.calories
#            quantity = self.comestible.ingredient.reference_quantity
#        elif self.comestible.child_model == 'D':
#            calories = self.comestible.dish.get_dish_calories()
#            quantity = self.comestible.dish.total_quantity
#        else:
#            return "This is an eating of nothingness" # should raise an exception - which?
#        eating_calories = self.quantity * calories / quantity
#        return eating_calories

#################################

#class DishForm(ModelForm):
#    class Meta: 
#        model = Dish


# use aggregate() to calculate calories etc from ingredients
# use annotate() to show values for each ingredient


##### move clagginess into a ratings app later
##    CLAGGINESS_CHOICES = (
##        ('A', 'anti-clag'),
##        ('B', 'balanced'), # better name? bitclag?
##        ('C', 'clag')
##    )
##    clagginess = models.CharField(max_length=1, choices=CLAGGINESS_CHOICES, blank=True) # totes subjective opinion :)

