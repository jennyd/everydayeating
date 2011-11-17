import datetime

from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.forms.models import ModelForm
from django.test import TestCase

from food.models import validate_positive, validate_positive_or_zero, Ingredient
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

    def test_login(self):
        # Create a user first.
        user = User.objects.create_user('jenny', 'jenny@example.com', 'jenny')
#        self.client.login(username='jenny', password='jenny')
#        self.client.logout()
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.templates), 2)
        self.assertTemplateUsed(response, 'food/login.html')
        self.assertTemplateUsed(response, 'food/base.html')
        # Not sure if it's necessary to check these - should all be provided by
        # django.contrib.auth.views.login
        self.assertTrue('csrf_token' in response.context)
        self.assertTrue('form' in response.context)

        response = self.client.post(reverse('login'),
                                    data={'username': 'jenny',
                                          'password': 'jenny'},
                                    follow=False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(response.templates), 0)
        response = self.client.post(reverse('login'),
                                    data={'username': 'jenny',
                                          'password': 'jenny'},
                                    follow=True)
#        print response.redirect_chain
        # Redirects through a 404 here...
        #### This isn't complete - login and logout aren't being done as shown
        #### in the documentation - fix it first

#        self.assertTemplateUsed(response, 'food/login.html')
#        self.assertTemplateUsed(response, 'food/base.html')

    def test_logout(self):
        #### This isn't complete - login and logout aren't being done as shown
        #### in the documentation - fix it first
        pass

    def test_ingredient_list(self):
        response = self.client.get(reverse('ingredient_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.templates), 2)
        self.assertTemplateUsed(response, 'food/ingredient_list.html')
        self.assertTemplateUsed(response, 'food/base.html')
        self.assertTrue('ingredient_list' in response.context)

    def test_ingredient_add(self):
        response = self.client.get(reverse('ingredient_add'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.templates), 2)
        self.assertTemplateUsed(response, 'food/ingredient_form.html')
        self.assertTemplateUsed(response, 'food/base.html')
        self.assertTrue('form' in response.context)
        # Is this necessary? The form is created by the generic view anyway...
        self.assertIsInstance(response.context['form'], ModelForm)

        # Add a good ingredient
        response = self.client.post(reverse('ingredient_add'),
                                    data={'name': 'Test ingredient good',
                                          'quantity': 100,
                                          'unit': 'g',
                                          'calories': 75},
                                    follow=True)
#        print response.redirect_chain
        # Add more here to check redirects?
        # Redirects to ingredient_list
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.templates), 2)
        self.assertTemplateUsed(response, 'food/ingredient_list.html')
        self.assertTemplateUsed(response, 'food/base.html')
        ingredient = Ingredient.objects.get(name='Test ingredient good')
        # is_dish should be set to False on save (default True)
        self.assertFalse(ingredient.is_dish)

        # Try to add bad ingredients

        # Send invalid quantity and calories values
        # Why doesn't this raise a ValidationError?
        response = self.client.post(reverse('ingredient_add'),
                                    data={'name': 'Test ingredient bad',
                                          'quantity': 0,
                                          'unit': 'g',
                                          'calories': -75})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.templates), 2)
        self.assertTemplateUsed(response, 'food/ingredient_form.html')
        self.assertTemplateUsed(response, 'food/base.html')
        self.assertTrue(u'Enter a number greater than 0' in
                                response.context['form']['quantity'].errors)
        self.assertTrue(u'Enter a number not less than 0' in
                                response.context['form']['calories'].errors)
        self.assertRaises(ObjectDoesNotExist, Ingredient.objects.get,
                                name='Test ingredient bad')

    def test_ingredient_detail(self):
        ingredient = Ingredient.objects.create(name = 'Test ingredient',
                                               quantity = 100,
                                               unit = 'g',
                                               calories = 75)
        response = self.client.get(reverse('ingredient_detail', kwargs={'pk': ingredient.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.templates), 2)
        self.assertTemplateUsed(response, 'food/ingredient_detail.html')
        self.assertTemplateUsed(response, 'food/base.html')
        self.assertTrue('ingredient' in response.context)

        # Try to display an ingredient which doesn't exist
        response = self.client.get(reverse('ingredient_detail', kwargs={'pk': 9999999999}))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

    def test_dish_list(self):
        response = self.client.get(reverse('dish_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.templates), 2)
        self.assertTemplateUsed(response, 'food/dish_list.html')
        self.assertTemplateUsed(response, 'food/base.html')
        self.assertTrue('dish_list' in response.context)

    def test_meal_list(self):
        response = self.client.get(reverse('meal_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.templates), 2)
        self.assertTemplateUsed(response, 'food/meal_list.html')
        self.assertTemplateUsed(response, 'food/base.html')
        self.assertTrue('meal_list' in response.context)


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

