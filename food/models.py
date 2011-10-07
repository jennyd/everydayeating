from django.db import models
from django.forms import ModelForm


UNIT_CHOICES = (
        ('g', 'grams'),
        ('ml', 'millilitres'),
        ('items', 'items') # units for stock pots, tea with milk, eggs, garlic cloves etc - better name?
    )


class Comestible(models.Model):

    def __unicode__(self):
        if self.child_model == 'I':
            return u"Ingredient: "+self.ingredient.name
        elif self.child_model == 'D':
            return u"Dish: "+self.dish.name
        else:
            return u"Child model field is useless" # should raise an exception - which?

    unit = models.CharField(max_length=5, choices=UNIT_CHOICES, default="g")

    CHILD_MODEL_CHOICES = (
        ('I', 'Ingredient'),
        ('D', 'Dish'),
    )
    child_model = models.CharField(max_length=1, choices=CHILD_MODEL_CHOICES, editable=False, default='D')


class Ingredient(Comestible):
    name = models.CharField(max_length=200, unique=True)

    def __unicode__(self):
        return self.name

    reference_quantity = models.DecimalField("the quantity to which the calorie value refers", max_digits=6, decimal_places=2, default=100)
    calories = models.DecimalField(max_digits=6, decimal_places=2)
    # add other nutrients to track later? fat, calories from carbs etc

    def save(self, *args, **kwargs):
        self.child_model = 'I' # so that the related comestible knows this is an ingredient
        super(Ingredient, self).save(*args, **kwargs) # Call the "real" save() method.


class Dish(Comestible):
    name = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name

    total_quantity = models.DecimalField("the total quantity of the finished dish", max_digits=6, decimal_places=2, blank=True)
    date_cooked = models.DateField("the date on which the dish is cooked") # default...

    def get_dish_calories(self):
        return sum(amount.get_amount_calories() for amount in self.contained_comestibles_set.all())

    class Meta:
        verbose_name_plural = "dishes"


class Amount(models.Model):

    def __unicode__(self):
        return unicode(self.contained_comestible)

    containing_dish = models.ForeignKey(Dish, related_name='contained_comestibles_set')
    contained_comestible = models.ForeignKey(Comestible, related_name='containing_dishes_set')
    quantity = models.DecimalField("the quantity of this ingredient in the dish, in ingredient units", max_digits=6, decimal_places=2, blank=True, null=True, default=0)

    def get_amount_calories(self):
        try:
            calories = self.contained_comestible.ingredient.calories
            ref_quantity = self.contained_comestible.ingredient.reference_quantity
        except Ingredient.DoesNotExist:
            try:
                calories = self.contained_comestible.dish.get_dish_calories()
                ref_quantity = self.contained_comestible.dish.total_quantity
            except Dish.DoesNotExist:
                raise Comestible.DoesNotExist, "This is an amount of nothingness"
        amount_calories = self.quantity * calories / ref_quantity
        return amount_calories


class Meal(models.Model):

    def __unicode__(self):
        return self.name+u" on "+unicode(self.date)

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
    comestibles = models.ManyToManyField(Comestible, through='Eating')


class Eating(models.Model):

    def __unicode__(self):
        return unicode(self.comestible)

    comestible = models.ForeignKey(Comestible)
    meal = models.ForeignKey(Meal)
    quantity = models.DecimalField("the quantity eaten", max_digits=6, decimal_places=2)



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

