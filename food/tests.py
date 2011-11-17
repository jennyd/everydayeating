import datetime

from django.core.urlresolvers import reverse
from django.test.client import Client
from django.utils import unittest # to make sure it's using the new unittest2

from food.views import get_week_starts_in_month


class FoodViewsTestCase(unittest.TestCase):
    def test_food_index(self):
        c = Client()
        response = c.get(reverse('food_index'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.templates), 2)
        self.assertEqual(response.templates[0].name, 'food/food_index.html')
        self.assertEqual(response.templates[1].name, 'food/base.html')
#        print response.templates
#        for template in response.templates:
#            print template.name
#        print response.context


class DateViewsTestCase(unittest.TestCase):
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

