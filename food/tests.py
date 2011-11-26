import datetime

from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.forms.models import ModelForm
from django.test import TestCase

from food.models import validate_positive, validate_positive_or_zero, Household, Comestible, Ingredient, Dish, Amount
from food.views import get_week_starts_in_month


fake_pk = 9999999999

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

################################################################################
# Ingredient views tests

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
        # FIXME Add more here to check redirects?
        # Redirects to ingredient_list
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.templates), 2)
        self.assertTemplateUsed(response, 'food/ingredient_list.html')
        self.assertTemplateUsed(response, 'food/base.html')
        ingredient = Ingredient.objects.get(name='Test ingredient good')
        # is_dish should be set to False on save (default True)
        self.assertFalse(ingredient.is_dish)

        # Try to add an ingredient with invalid quantity and calories values
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
        response = self.client.get(reverse('ingredient_detail',
                                           kwargs={'pk': ingredient.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.templates), 2)
        self.assertTemplateUsed(response, 'food/ingredient_detail.html')
        self.assertTemplateUsed(response, 'food/base.html')
        self.assertTrue('ingredient' in response.context)

        # Try to display an ingredient which doesn't exist
        response = self.client.get(reverse('ingredient_detail',
                                           kwargs={'pk': fake_pk}))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

    def test_ingredient_edit(self):
        ingredient = Ingredient.objects.create(name = 'Test ingredient',
                                               quantity = 100,
                                               unit = 'g',
                                               calories = 75)
        response = self.client.get(reverse('ingredient_edit',
                                           kwargs={'pk': ingredient.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.templates), 2)
        self.assertTemplateUsed(response, 'food/ingredient_form.html')
        self.assertTemplateUsed(response, 'food/base.html')
        self.assertTrue('ingredient' in response.context)
        self.assertTrue('form' in response.context)
        # Is this necessary? The form is created by the generic view anyway...
        self.assertIsInstance(response.context['form'], ModelForm)

        # Edit an ingredient correctly
        response = self.client.post(reverse('ingredient_edit',
                                           kwargs={'pk': ingredient.id}),
                                    data={'name': 'Test ingredient',
                                          'quantity': 100,
                                          'unit': 'g',
                                          'calories': 5},
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.templates), 2)
        # Redirects to ingredient_list
        self.assertTemplateUsed(response, 'food/ingredient_list.html')
        self.assertTemplateUsed(response, 'food/base.html')
        ingredient = Ingredient.objects.get(pk=ingredient.id)
        self.assertEqual(ingredient.calories, 5)

        # Try to edit an ingredient with invalid quantity and calories values
        response = self.client.post(reverse('ingredient_edit',
                                           kwargs={'pk': ingredient.id}),
                                    data={'quantity': 0,
                                          'calories': -75},
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.templates), 2)
        self.assertTemplateUsed(response, 'food/ingredient_form.html')
        self.assertTemplateUsed(response, 'food/base.html')
        self.assertTrue(u'Enter a number greater than 0' in
                                response.context['form']['quantity'].errors)
        self.assertTrue(u'Enter a number not less than 0' in
                                response.context['form']['calories'].errors)
        # FIXME Check that the ingredient still has its initial values

        # Try to edit an ingredient which doesn't exist
        self.assertRaises(ObjectDoesNotExist, Ingredient.objects.get,
                                                      pk=fake_pk)
        response = self.client.get(reverse('ingredient_edit',
                                           kwargs={'pk': fake_pk}))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

    def test_ingredient_delete(self):
        ingredient = Ingredient.objects.create(name = 'Test ingredient',
                                               quantity = 100,
                                               unit = 'g',
                                               calories = 75)
        response = self.client.get(reverse('ingredient_delete',
                                           kwargs={'pk': ingredient.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.templates), 2)
        self.assertTemplateUsed(response, 'food/ingredient_confirm_delete.html')
        self.assertTemplateUsed(response, 'food/base.html')
        self.assertTrue('ingredient' in response.context)

        # Delete an ingredient
        response = self.client.post(reverse('ingredient_delete',
                                           kwargs={'pk': ingredient.id}),
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.templates), 2)
        # Redirects to ingredient_list
        self.assertTemplateUsed(response, 'food/ingredient_list.html')
        self.assertTemplateUsed(response, 'food/base.html')
        self.assertRaises(ObjectDoesNotExist, Ingredient.objects.get,
                                        pk=ingredient.id)

        # Try to delete an ingredient which doesn't exist
        self.assertRaises(ObjectDoesNotExist, Ingredient.objects.get,
                                                      pk=fake_pk)
        response = self.client.get(reverse('ingredient_delete',
                                           kwargs={'pk': fake_pk}))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

    def test_ingredient_manage(self):
        ingredient_one = Ingredient.objects.create(name = 'Test ingredient 1',
                                               quantity = 100,
                                               unit = 'g',
                                               calories = 75)
        ingredient_two = Ingredient.objects.create(name = 'Test ingredient 2',
                                               quantity = 100,
                                               unit = 'ml',
                                               calories = 828)
        response = self.client.get(reverse('ingredient_manage'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.templates), 2)
        self.assertTemplateUsed(response, 'food/ingredient_manage.html')
        self.assertTemplateUsed(response, 'food/base.html')
        self.assertTrue('formset' in response.context)
        # FIXME what is this formset?
        # self.assertIsInstance(response.context['formset'], #### )
        # FIXME Check that it's using RequestContext

        # Edit an ingredient correctly
        response = self.client.post(reverse('ingredient_manage'),
                                    data={'form-TOTAL_FORMS': 5,
                                          'form-INITIAL_FORMS': 2,
                                          'form-0-comestible_ptr': ingredient_one.id,
                                          'form-0-name': 'Test ingredient 1',
                                          'form-0-quantity': 100,
                                          'form-0-unit': 'g',
                                          'form-0-calories': 5, # was 75
                                          'form-1-comestible_ptr': ingredient_two.id,
                                          'form-1-name': 'Test ingredient 2',
                                          'form-1-quantity': 100,
                                          'form-1-unit': 'ml',
                                          'form-1-calories': 828,
                                          # Leave the default values for these
                                          # fields unchanged
                                          'form-2-quantity': 100,
                                          'form-2-unit': 'g',
                                          'form-3-quantity': 100,
                                          'form-3-unit': 'g',
                                          'form-4-quantity': 100,
                                          'form-4-unit': 'g'},
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.templates), 2)
        # Redirects to ingredient_list
        self.assertTemplateUsed(response, 'food/ingredient_list.html')
        self.assertTemplateUsed(response, 'food/base.html')
        ingredient = Ingredient.objects.get(pk=ingredient_one.id)
        self.assertEqual(ingredient.calories, 5)

        # Try to edit an ingredient with invalid quantity and calories values
        response = self.client.post(reverse('ingredient_manage'),
                                    data={'form-TOTAL_FORMS': 5,
                                          'form-INITIAL_FORMS': 2,
                                          'form-0-comestible_ptr': ingredient_one.id,
                                          'form-0-name': 'Test ingredient 1',
                                          'form-0-quantity': 0, # was 100
                                          'form-0-unit': 'g',
                                          'form-0-calories': -75, # was 5
                                          'form-1-comestible_ptr': ingredient_two.id,
                                          'form-1-name': 'Test ingredient 2',
                                          'form-1-quantity': 100,
                                          'form-1-unit': 'ml',
                                          'form-1-calories': 828,
                                          # Leave the default values for these
                                          # fields unchanged
                                          'form-2-quantity': 100,
                                          'form-2-unit': 'g',
                                          'form-3-quantity': 100,
                                          'form-3-unit': 'g',
                                          'form-4-quantity': 100,
                                          'form-4-unit': 'g'},
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.templates), 2)
        self.assertTemplateUsed(response, 'food/ingredient_manage.html')
        self.assertTemplateUsed(response, 'food/base.html')
        self.assertTrue(u'Enter a number greater than 0' in
                                response.context['formset'][0]['quantity'].errors)
        self.assertTrue(u'Enter a number not less than 0' in
                                response.context['formset'][0]['calories'].errors)
        # FIXME Check that the ingredient still has its initial values

        # Try to send a comestible_ptr which doesn't exist
        self.assertRaises(ObjectDoesNotExist, Ingredient.objects.get,
                                                      pk=fake_pk)
        self.assertRaises(ObjectDoesNotExist, Comestible.objects.get,
                                                      pk=fake_pk)
        response = self.client.post(reverse('ingredient_manage'),
                                    data={'form-TOTAL_FORMS': 5,
                                          'form-INITIAL_FORMS': 2,
                                          'form-0-comestible_ptr': ingredient_one.id,
                                          'form-0-name': 'Test ingredient 1',
                                          'form-0-quantity': 100,
                                          'form-0-unit': 'g',
                                          'form-0-calories': 5,
                                          'form-1-comestible_ptr': fake_pk,
                                          'form-1-name': 'Test ingredient 2',
                                          'form-1-quantity': 100,
                                          'form-1-unit': 'ml',
                                          'form-1-calories': 828,
                                          # Leave the default values for these
                                          # fields unchanged
                                          'form-2-quantity': 100,
                                          'form-2-unit': 'g',
                                          'form-3-quantity': 100,
                                          'form-3-unit': 'g',
                                          'form-4-quantity': 100,
                                          'form-4-unit': 'g'},
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.templates), 2)
        self.assertTemplateUsed(response, 'food/ingredient_manage.html')
        self.assertTemplateUsed(response, 'food/base.html')
        # FIXME Check errors here

################################################################################
# Dish views tests

    def test_dish_list(self):
        response = self.client.get(reverse('dish_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.templates), 2)
        self.assertTemplateUsed(response, 'food/dish_list.html')
        self.assertTemplateUsed(response, 'food/base.html')
        self.assertTrue('dish_list' in response.context)

    def test_dish_detail(self):
        # Create a user, household, ingredients, dish & amounts
        test_user = User.objects.create(username = 'testuser',
                                        password = 'testpassword')
        test_household = Household.objects.create(name = 'Test household',
                                             admin = test_user)
        ingredient_one = Ingredient.objects.create(name = 'Test ingredient 1',
                                               quantity = 100,
                                               unit = 'g',
                                               calories = 75)
        ingredient_two = Ingredient.objects.create(name = 'Test ingredient 2',
                                               quantity = 100,
                                               unit = 'ml',
                                               calories = 828)
        dish = Dish.objects.create(name = 'Test dish',
                                   quantity = 500,
                                   date_cooked = datetime.date.today(),
                                   household = test_household,
                                   recipe_url = u'http://www.example.com/recipeurl/',
                                   unit = 'g')
        dish.cooks.add(test_user)
        dish.contained_comestibles_set.create(contained_comestible = ingredient_one,
                                              quantity = 50)
        dish.contained_comestibles_set.create(contained_comestible = ingredient_two,
                                              quantity = 150)

        response = self.client.get(reverse('dish_detail',
                                           kwargs={'pk': dish.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.templates), 2)
        self.assertTemplateUsed(response, 'food/dish_detail.html')
        self.assertTemplateUsed(response, 'food/base.html')
        self.assertTrue('dish' in response.context)

        # Try to display a dish which doesn't exist
        self.assertRaises(ObjectDoesNotExist, Dish.objects.get, pk=fake_pk)
        response = self.client.get(reverse('dish_detail',
                                           kwargs={'pk': fake_pk}))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

    def test_dish_delete(self):
        # Create a user, household, ingredients, dish & amounts
        test_user = User.objects.create(username = 'testuser',
                                        password = 'testpassword')
        test_household = Household.objects.create(name = 'Test household',
                                             admin = test_user)
        ingredient_one = Ingredient.objects.create(name = 'Test ingredient 1',
                                               quantity = 100,
                                               unit = 'g',
                                               calories = 75)
        ingredient_two = Ingredient.objects.create(name = 'Test ingredient 2',
                                               quantity = 100,
                                               unit = 'ml',
                                               calories = 828)
        dish = Dish.objects.create(name = 'Test dish',
                                   quantity = 500,
                                   date_cooked = datetime.date.today(),
                                   household = test_household,
                                   recipe_url = u'http://www.example.com/recipeurl/',
                                   unit = 'g')
        dish.cooks.add(test_user)
        dish.contained_comestibles_set.create(contained_comestible = ingredient_one,
                                              quantity = 50)
        dish.contained_comestibles_set.create(contained_comestible = ingredient_two,
                                              quantity = 150)

        response = self.client.get(reverse('dish_delete',
                                           kwargs={'pk': dish.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.templates), 2)
        self.assertTemplateUsed(response, 'food/dish_confirm_delete.html')
        self.assertTemplateUsed(response, 'food/base.html')
        self.assertTrue('dish' in response.context)

        # Delete a dish (and its amounts via cascade)
        response = self.client.post(reverse('dish_delete',
                                           kwargs={'pk': dish.id}),
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.templates), 2)
        # Redirects to dish_list
        self.assertTemplateUsed(response, 'food/dish_list.html')
        self.assertTemplateUsed(response, 'food/base.html')
        self.assertRaises(ObjectDoesNotExist, Dish.objects.get,
                                        pk=dish.id)
        self.assertRaises(ObjectDoesNotExist, Amount.objects.get,
                                        containing_dish=dish.id)

        # Try to delete a dish which doesn't exist
        self.assertRaises(ObjectDoesNotExist, Dish.objects.get,
                                                      pk=fake_pk)
        response = self.client.get(reverse('dish_delete',
                                           kwargs={'pk': fake_pk}))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

    def test_dish_add(self):
        # Create a user, household and ingredients
        # Use setUp for this instead of fixtures?
        test_user = User.objects.create(username = 'testuser',
                                        password = 'testpassword')
        test_household = Household.objects.create(name = 'Test household',
                                             admin = test_user)
        ingredient_one = Ingredient.objects.create(name = 'Test ingredient 1',
                                               quantity = 100,
                                               unit = 'g',
                                               calories = 75)
        ingredient_two = Ingredient.objects.create(name = 'Test ingredient 2',
                                               quantity = 100,
                                               unit = 'ml',
                                               calories = 828)

        response = self.client.get(reverse('dish_add'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.templates), 2)
        self.assertTemplateUsed(response, 'food/dish_edit.html')
        self.assertTemplateUsed(response, 'food/base.html')
        self.assertTrue('form' in response.context)
        self.assertTrue('formset' in response.context)
        # Is this necessary?
        self.assertIsInstance(response.context['form'], ModelForm)
        # self.assertIsInstance(response.context['formset'], # ???? )

        # Add a good dish with amounts
        response = self.client.post(reverse('dish_add'),
                                    data={'name': 'Test dish',
                                          'quantity': 500,
                                          'date_cooked': datetime.date.today(),
                                          'household': test_household.id,
                                          'recipe_url': u'http://www.example.com/recipeurl/',
                                          'cooks': test_user.id,
                                          'unit': 'g',
                                          'contained_comestibles_set-TOTAL_FORMS': 6,
                                          'contained_comestibles_set-INITIAL_FORMS': 0,
                                          'contained_comestibles_set-0-contained_comestible': 1,
                                          'contained_comestibles_set-0-quantity': 50,
                                          # Leave the default values for these
                                          # fields unchanged
                                          'contained_comestibles_set-1-quantity': 0,
                                          'contained_comestibles_set-2-quantity': 0,
                                          'contained_comestibles_set-3-quantity': 0,
                                          'contained_comestibles_set-4-quantity': 0,
                                          'contained_comestibles_set-5-quantity': 0},
                                    follow=True)
#        print response.redirect_chain
        # FIXME Add more here to check redirects?
        # Redirects to dish_detail
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.templates), 2)
        self.assertTemplateUsed(response, 'food/dish_detail.html')
        self.assertTemplateUsed(response, 'food/base.html')
        # Check dish & amounts created correctly

        # Try to add a dish and an amount with invalid quantity values
        response = self.client.post(reverse('dish_add'),
                                    data={'name': 'Test dish bad',
                                          'quantity': 0,
                                          'date_cooked': datetime.date.today(),
                                          'household': test_household.id,
                                          'recipe_url': u'http://www.example.com/recipeurl/',
                                          'cooks': test_user.id,
                                          'unit': 'g',
                                          'contained_comestibles_set-TOTAL_FORMS': 6,
                                          'contained_comestibles_set-INITIAL_FORMS': 0,
                                          'contained_comestibles_set-0-contained_comestible': 1,
                                          'contained_comestibles_set-0-quantity': -1,
                                          # Leave the default values for these
                                          # fields unchanged
                                          'contained_comestibles_set-1-quantity': 0,
                                          'contained_comestibles_set-2-quantity': 0,
                                          'contained_comestibles_set-3-quantity': 0,
                                          'contained_comestibles_set-4-quantity': 0,
                                          'contained_comestibles_set-5-quantity': 0})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.templates), 2)
        self.assertTemplateUsed(response, 'food/dish_edit.html')
        self.assertTemplateUsed(response, 'food/base.html')
        self.assertTrue(u'Enter a number greater than 0' in
                                response.context['form']['quantity'].errors)
        self.assertTrue(u'Enter a number not less than 0' in
                                response.context['formset'][0]['quantity'].errors)
        self.assertRaises(ObjectDoesNotExist, Dish.objects.get,
                                name='Test dish bad')

    def test_dish_edit(self):
        # Create a user, household, ingredients, dish & amounts
        test_user = User.objects.create(username = 'testuser',
                                        password = 'testpassword')
        test_household = Household.objects.create(name = 'Test household',
                                             admin = test_user)
        ingredient_one = Ingredient.objects.create(name = 'Test ingredient 1',
                                               quantity = 100,
                                               unit = 'g',
                                               calories = 75)
        ingredient_two = Ingredient.objects.create(name = 'Test ingredient 2',
                                               quantity = 100,
                                               unit = 'ml',
                                               calories = 828)
        dish = Dish.objects.create(name = 'Test dish',
                                   quantity = 500,
                                   date_cooked = datetime.date.today(),
                                   household = test_household,
                                   recipe_url = u'http://www.example.com/recipeurl/',
                                   unit = 'g')
        dish.cooks.add(test_user)
        dish.contained_comestibles_set.create(contained_comestible = ingredient_one,
                                              quantity = 50)
        dish.contained_comestibles_set.create(contained_comestible = ingredient_two,
                                              quantity = 150)

        response = self.client.get(reverse('dish_edit', kwargs={'dish_id': dish.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.templates), 2)
        self.assertTemplateUsed(response, 'food/dish_edit.html')
        self.assertTemplateUsed(response, 'food/base.html')
        self.assertTrue('form' in response.context)
        self.assertTrue('formset' in response.context)
        # Is this necessary?
        self.assertIsInstance(response.context['form'], ModelForm)
        # self.assertIsInstance(response.context['formset'], # ???? )

        # Edit a dish correctly
        response = self.client.post(reverse('dish_edit',
                                            kwargs={'dish_id': dish.id}),
                                    data={'name': 'Test dish',
                                          'quantity': 400, # was 500
                                          'date_cooked': datetime.date.today(),
                                          'household': test_household.id,
                                          'recipe_url': u'http://www.example.com/recipeurl/',
                                          'cooks': test_user.id,
                                          'unit': 'ml', # was 'g'
                                          'contained_comestibles_set-TOTAL_FORMS': 6,
                                          'contained_comestibles_set-INITIAL_FORMS': 0,
                                          'contained_comestibles_set-0-contained_comestible': 1,
                                          'contained_comestibles_set-0-quantity': 50,
                                          'contained_comestibles_set-1-contained_comestible': 2,
                                          'contained_comestibles_set-1-quantity': 180, # was 150
                                          # Leave the default values for these
                                          # fields unchanged
                                          'contained_comestibles_set-2-quantity': 0,
                                          'contained_comestibles_set-3-quantity': 0,
                                          'contained_comestibles_set-4-quantity': 0,
                                          'contained_comestibles_set-5-quantity': 0},
                                    follow=True)
#        print response.redirect_chain
        # FIXME Add more here to check redirects?
        # Redirects to dish_detail
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.templates), 2)
        self.assertTemplateUsed(response, 'food/dish_detail.html')
        self.assertTemplateUsed(response, 'food/base.html')
        # Check dish & amounts edited correctly

        # Try to edit a dish and an amount with invalid quantity values
        response = self.client.post(reverse('dish_edit',
                                            kwargs={'dish_id': dish.id}),
                                    data={'name': 'Test dish',
                                          'quantity': 0, # was 500, then edited to 400
                                          'date_cooked': datetime.date.today(),
                                          'household': test_household.id,
                                          'recipe_url': u'http://www.example.com/recipeurl/',
                                          'cooks': test_user.id,
                                          'unit': 'ml', # was 'g', then edited to 'ml'
                                          'contained_comestibles_set-TOTAL_FORMS': 6,
                                          'contained_comestibles_set-INITIAL_FORMS': 0,
                                          'contained_comestibles_set-0-contained_comestible': 1,
                                          'contained_comestibles_set-0-quantity': 50,
                                          'contained_comestibles_set-1-contained_comestible': 2,
                                          'contained_comestibles_set-1-quantity': -100, # was 150, then edited to 180
                                          # Leave the default values for these
                                          # fields unchanged
                                          'contained_comestibles_set-2-quantity': 0,
                                          'contained_comestibles_set-3-quantity': 0,
                                          'contained_comestibles_set-4-quantity': 0,
                                          'contained_comestibles_set-5-quantity': 0})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.templates), 2)
        self.assertTemplateUsed(response, 'food/dish_edit.html')
        self.assertTemplateUsed(response, 'food/base.html')
        self.assertTrue(u'Enter a number greater than 0' in
                                response.context['form']['quantity'].errors)
        self.assertTrue(u'Enter a number not less than 0' in
                                response.context['formset'][1]['quantity'].errors)

################################################################################
# Meal views tests

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

