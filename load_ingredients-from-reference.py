# Full path and name to your csv file
csv_filepathname="/home/jenny/Python/everydayeating/ingredients-from-reference.csv"
# Full path to your django project directory
your_djangoproject_home="/home/jenny/Python/everydayeating/"

import sys,os
sys.path.append(your_djangoproject_home)
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from food.models import Ingredient

import csv
dataReader = csv.reader(open(csv_filepathname), delimiter=',', quotechar='"')

for row in dataReader:
    if row[0] != 'Name': # Ignore the header row, import everything else
        ingredient = Ingredient()
        ingredient.name = row[0]
        ingredient.quantity = row[1]
        ingredient.calories = row[2]
        ingredient.unit = row[3]
        ingredient.save()
        print ingredient.id, ingredient.name
