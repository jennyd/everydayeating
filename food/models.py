from django.db import models



class Nutrition(models.Model):
    name = models.CharField(max_length=200, unique=True)
    def __unicode__(self):
        return self.name
    calories = models.DecimalField(max_digits=6, decimal_places=2)
    # add other nutrients to track later? fat, calories from carbs etc
    
    CLAGGINESS_CHOICES = (
        ('A', 'anti-clag'),
        ('B', 'balanced'), # better name? bitclag?
        ('C', 'clag')
    )
    clagginess = models.CharField(max_length=1, choices=CLAGGINESS_CHOICES, blank=True) # totes subjective opinion :)

    
    class Meta:
        abstract = True



class Food(Nutrition):
    reference_quantity = models.DecimalField("the quantity to which the calorie value refers", max_digits=6, decimal_places=2, default=100)
    REFERENCE_QUANTITY_UNIT_CHOICES = (
        ('g', 'grams'),
        ('ml', 'millilitres'),
        ('items', 'items') # units for stock pots, tea with milk, eggs, garlic cloves etc - better name?
    )
    reference_quantity_unit = models.CharField(max_length=5, choices=REFERENCE_QUANTITY_UNIT_CHOICES, default="g")



# only for dishes: use a Dish(Food) proxy model? not sure how that would work with ManyToManyField...
#    is_dish = models.BooleanField() # default value?
#    ingredients = models.ManyToManyField('self', symmetrical=False, blank=True) # how to make sure that a dish doesn't have itself as an ingredient?
#    total_quantity = models.DecimalField(max_digits=6, decimal_places=2, blank=True)

    # use aggregate() to calculate calories etc from ingredients
    # use annotate() to show values for each ingredient



# class Meal(Nutrition):
    # name to be generated from date + breakfast/lunch/tea/dinner/snack
    # date = ...




