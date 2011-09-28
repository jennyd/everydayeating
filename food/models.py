from django.db import models
from django.forms import ModelForm


UNIT_CHOICES = (
        ('g', 'grams'),
        ('ml', 'millilitres'),
        ('items', 'items') # units for stock pots, tea with milk, eggs, garlic cloves etc - better name?
    )


#class Nutrition(models.Model):
##### move clagginess into a ratings app later
##    CLAGGINESS_CHOICES = (
##        ('A', 'anti-clag'),
##        ('B', 'balanced'), # better name? bitclag?
##        ('C', 'clag')
##    )
##    clagginess = models.CharField(max_length=1, choices=CLAGGINESS_CHOICES, blank=True) # totes subjective opinion :)
    
#    class Meta:
#        abstract = True



#class Ingredient(Nutrition):
#    name = models.CharField(max_length=200, unique=True)
#    def __unicode__(self):
#        return self.name
#    reference_quantity = models.DecimalField("the quantity to which the calorie value refers", max_digits=6, decimal_places=2, default=100)
#    reference_quantity_unit = models.CharField(max_length=5, choices=UNIT_CHOICES, default="g")
#    calories = models.DecimalField(max_digits=6, decimal_places=2)
#    # add other nutrients to track later? fat, calories from carbs etc


#class IngredientForm(ModelForm):
#    class Meta: 
#        model = Ingredient



#class Dish(Nutrition):
#    name = models.CharField(max_length=200)
#    def __unicode__(self):
#        return self.name
#    total_quantity = models.DecimalField("the total quantity of the finished dish", max_digits=6, decimal_places=2, blank=True)
#    total_quantity_unit = models.CharField(max_length=5, choices=UNIT_CHOICES, default="g")
#    date_cooked = models.DateField("the date on which the dish is cooked") # default...

#    class Meta:
#        verbose_name_plural = "dishes"


#class DishForm(ModelForm):
#    class Meta: 
#        model = Dish



#class Amount(models.Model):
#    def __unicode__(self):
#        return self.ingredient.name
#    containing_dish = models.ForeignKey(Dish, related_name='contained_amounts_set')
#    quantity = models.DecimalField("the quantity of this ingredient in the dish, in ingredient units", max_digits=6, #decimal_places=2, blank=True)
#    ingredient = models.ForeignKey(Ingredient, null=True, blank=True)
#    dish_as_ingredient = models.ForeignKey(Dish, related_name='amounts_using_set', null=True, blank=True)


#class AmountForm(ModelForm):
#    class Meta: 
#        model = Amount

#################################################

class Comestible(models.Model):
    def __unicode__(self):
        if self.ingredient:
            return self.ingredient.name
        else:
            return self.dish.name



class Ingredient(Comestible):
    name = models.CharField(max_length=200, unique=True)
    def __unicode__(self):
        return self.name
    reference_quantity = models.DecimalField("the quantity to which the calorie value refers", max_digits=6, decimal_places=2, default=100)
    reference_quantity_unit = models.CharField(max_length=5, choices=UNIT_CHOICES, default="g")
    calories = models.DecimalField(max_digits=6, decimal_places=2)
    # add other nutrients to track later? fat, calories from carbs etc



class Dish(Comestible):
    name = models.CharField(max_length=200)
    def __unicode__(self):
        return self.name
    total_quantity = models.DecimalField("the total quantity of the finished dish", max_digits=6, decimal_places=2, blank=True)
    total_quantity_unit = models.CharField(max_length=5, choices=UNIT_CHOICES, default="g")
    date_cooked = models.DateField("the date on which the dish is cooked") # default...

    class Meta:
        verbose_name_plural = "dishes"



class Amount(models.Model):
    def __unicode__(self):
        return self.contained_comestible.name
#    containing_dish = models.ForeignKey(Dish, related_name='contained_amounts_set')
#    ingredient = models.ForeignKey(Ingredient, null=True, blank=True)
#    dish_as_ingredient = models.ForeignKey(Dish, related_name='amounts_using_set', null=True, blank=True)
    containing_dish = models.ForeignKey(Dish, related_name='contained_comestibles_set')
    contained_comestible = models.ForeignKey(Comestible, related_name='containing_dishes_set')
    quantity = models.DecimalField("the quantity of this ingredient in the dish, in ingredient units", max_digits=6, decimal_places=2, blank=True)



# only for dishes: use a Dish(Ingredient) proxy model? not sure how that would work with ManyToManyField...
#    is_dish = models.BooleanField() # default value?
#    ingredients = models.ManyToManyField('self', symmetrical=False, blank=True) # how to make sure that a dish doesn't have itself as an ingredient?
#    total_quantity = models.DecimalField(max_digits=6, decimal_places=2, blank=True)

    # use aggregate() to calculate calories etc from ingredients
    # use annotate() to show values for each ingredient



# class Meal(Nutrition):
    # name to be generated from date + breakfast/lunch/tea/dinner/snack
    # date = ...




