import datetime

from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.test import TestCase

from food.models import validate_positive, validate_positive_or_zero
from food.views import get_week_starts_in_month


class ValidatorsTestCase(TestCase):
    def test_validate_positive(self):
        validate_positive(1)
        self.assertRaises(ValidationError, validate_positive, 0)
        self.assertRaises(ValidationError, validate_positive, -1)
#        # This would be helpful if there were more than one point in the
#        # function where the exception could be raised, but it's not necessary
#        # here.
#        with self.assertRaises(ValidationError) as context:
#            validate_positive(0)
#            self.assertEqual(context.exception.message, u'Enter a number greater than 0')

    def test_validate_positive_or_zero(self):
        validate_positive_or_zero(1)
        validate_positive_or_zero(0)
        self.assertRaises(ValidationError, validate_positive, -1)


class FoodViewsTestCase(TestCase):
    def test_food_index(self):
        response = self.client.get(reverse('food_index'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.templates), 2)
        self.assertTemplateUsed(response, 'food/food_index.html')
        self.assertTemplateUsed(response, 'food/base.html')
#        print response.templates
#        for template in response.templates:
#            print template.name
#        print response.context

    def test_ingredient_list(self):
        response = self.client.get(reverse('ingredient_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.templates), 2)
        self.assertTemplateUsed(response, 'food/ingredient_list.html')
        self.assertTemplateUsed(response, 'food/base.html')
        self.assertTrue('ingredient_list' in response.context)
#        print response.templates
#        for template in response.templates:
#            print template.name
#        print response.context

    def test_dish_list(self):
        response = self.client.get(reverse('dish_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.templates), 2)
        self.assertTemplateUsed(response, 'food/dish_list.html')
        self.assertTemplateUsed(response, 'food/base.html')
        self.assertTrue('dish_list' in response.context)
#        print response.templates
#        for template in response.templates:
#            print template.name
#        print response.context

    def test_meal_list(self):
        response = self.client.get(reverse('meal_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.templates), 2)
        self.assertTemplateUsed(response, 'food/meal_list.html')
        self.assertTemplateUsed(response, 'food/base.html')
        self.assertTrue('meal_list' in response.context)
#        print response.templates
#        for template in response.templates:
#            print template.name
#        print response.context


class DateViewsTestCase(TestCase):
    def test_get_week_starts_in_month(self):
        # A normal month:
        month_start_date = datetime.datetime(2011, 11, 1, 0, 0)
        test_week_date_list = get_week_starts_in_month(month_start_date)
        expected_results = [datetime.datetime(2011, 10, 31, 0, 0),
                            datetime.datetime(2011, 11, 7, 0, 0),
                            datetime.datetime(2011, 11, 14, 0, 0),
                            datetime.datetime(2011, 11, 21, 0, 0),
                            datetime.datetime(2011, 11, 28, 0, 0)]
        self.assertEqual(test_week_date_list, expected_results)

        # December, to test moving into a new year
        month_start_date = datetime.datetime(2011, 12, 1, 0, 0)
        test_week_date_list = get_week_starts_in_month(month_start_date)
        expected_results = [datetime.datetime(2011, 11, 28, 0, 0),
                            datetime.datetime(2011, 12, 5, 0, 0),
                            datetime.datetime(2011, 12, 12, 0, 0),
                            datetime.datetime(2011, 12, 19, 0, 0),
                            datetime.datetime(2011, 12, 26, 0, 0)]
        self.assertEqual(test_week_date_list, expected_results)

