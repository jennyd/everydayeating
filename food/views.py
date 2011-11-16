import datetime
import sys

from django import forms
from django.core.exceptions import ValidationError
from django.shortcuts import HttpResponse, HttpResponseRedirect, render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.http import Http404
from django.views.generic import MonthArchiveView, WeekArchiveView, DayArchiveView
from django.forms.models import modelformset_factory, BaseInlineFormSet, inlineformset_factory

from food.models import Ingredient, Dish, DishForm, Amount, Meal, MealForm, Portion

def ingredient_manage(request):
    IngredientFormSet = modelformset_factory(Ingredient, extra=3)
    if request.method == 'POST':
        formset = IngredientFormSet(request.POST, request.FILES)
        if formset.is_valid():
            formset.save()
            return HttpResponseRedirect('/food/ingredients/')
    else:
        formset = IngredientFormSet()
    return render_to_response("food/ingredient_manage.html", {
        "formset": formset,},
        context_instance=RequestContext(request) # needed for csrf token
    )

def dish_amounts_form(request, dish_id=None):
    DishFormSet = inlineformset_factory(Dish, Amount,
            # I think fk_name shouldn't be needed any more, since Amount
            #  now has only one fk to Dish, but it does need to be here...
            fk_name="containing_dish", extra=6)
    if dish_id:
        dish = Dish.objects.get(pk=dish_id)
    else:
        dish = Dish()
    if request.method == 'POST':
        form = DishForm(request.POST, request.FILES, instance=dish)
        formset = DishFormSet(request.POST, request.FILES, instance=dish)
        if form.is_valid() and formset.is_valid():
            # dish can't calculate calories from amounts until they're saved...
            # but amounts need dish to be there first for fk...
            form.save() # do this only if not dish.id? or dish_id?
            formset.save()
            # don't need to save dish again here - signal receivers catch
            # amounts being saved or deleted and update dish for each one
            ## ... so save dish again after amounts are saved from the formset
            # dish.save()
            return redirect('dish_detail', dish.id)
    else:
        form = DishForm(instance=dish)
        formset = DishFormSet(instance=dish)
    return render_to_response("food/dish_edit.html", {
        "form": form,
        "formset": formset,
        "dish": dish,},
        context_instance=RequestContext(request) # needed for csrf token
    )

class BaseMealInlineFormSet(BaseInlineFormSet):
    def clean(self):
        '''
        Ensures that if there are multiple portions of a dish in a meal, their
        total quantity is not greater than the available quantity of the dish
        (the dish's remaining quantity plus the portions' saved quantities, if
        they exist).
        '''
        super(BaseInlineFormSet, self).clean()
        if any(self.errors):
            # Don't bother validating the formset unless each form is valid on
            # its own
            return
        # Make a list of dicts containing the comestible and quantity from each
        # (not deleted) form in the formset, and the portion's saved quantity
        # (set to 0 if it isn't yet saved)
        portions = []
        for form in self.forms:
            if (form not in self.deleted_forms) and form.cleaned_data:
                portion = {'comestible' : form.cleaned_data['comestible'],
                           'quantity': form.cleaned_data['quantity']}
                try:
                    saved_portion = Portion.objects.get(pk=form.instance.id)
                    portion['saved_quantity'] = saved_portion.quantity
                except Portion.DoesNotExist:
                    portion['saved_quantity'] = 0
                portions.append(portion)
        # Make a list of dicts containing each comestible only once with its
        # combined quantities and saved quantities
        unique_portions = []
        while portions:
            portion = portions.pop()
            for p in portions:
                if p['comestible'] == portion['comestible']:
                    portion['quantity'] += p['quantity']
                    portion['saved_quantity'] += p['saved_quantity']
                    portions.remove(p)
            unique_portions.append(portion)
        for p in unique_portions:
            # Compare the portion quantity to the available quantity of the dish
            # (mostly copied from Portion.clean()...)
            if p['comestible'].is_dish:
                dish = p['comestible'].dish
                remaining_quantity = dish.get_remaining_quantity()
                if (remaining_quantity + p['saved_quantity'] - p['quantity']) < 0:
                    unit = dish.unit
                    remaining_quantity += p['saved_quantity']
                    raise ValidationError, u"The remaining quantity of %s (%s %s) is less than the total quantity of it in this meal." % (dish, remaining_quantity, unit)


def meal_portion_form(request, meal_id=None):
    MealFormSet = inlineformset_factory(Meal, Portion, extra=6,
                                        formset=BaseMealInlineFormSet)
    if meal_id:
        meal = Meal.objects.get(pk=meal_id)
    else:
        meal = Meal()
    if request.method == 'POST':
        form = MealForm(request.POST, request.FILES, instance=meal)
        formset = MealFormSet(request.POST, request.FILES, instance=meal)
        if form.is_valid() and formset.is_valid():
            # meal can't calculate calories from portions until they're saved...
            # but portions need meal to be there first for fk...
            form.save() # do this only if not meal.id? or meal_id?
            formset.save()
            # don't need to save meal again here - signal receivers catch
            # portions being saved or deleted and update meal for each one
            ## ... so save meal again after portions are saved from the formset
            # meal.save()
            return redirect('meal_detail', meal.id)
    else:
        form = MealForm(instance=meal)
        formset = MealFormSet(instance=meal)
    return render_to_response("food/meal_edit.html", {
        "form": form,
        "formset": formset,
        "meal": meal,},
        context_instance=RequestContext(request) # needed for csrf token
    )

class DishMultiplyForm(forms.Form):
    # form for entry/selection of multiplication factor for amounts
    OPERATION_CHOICES = (
        ('multiply', 'multiply'),
        ('divide', 'divide'),
    )
    operation = forms.ChoiceField(choices=OPERATION_CHOICES, initial='multiply')
    factor = forms.DecimalField()

def dish_multiply(request, dish_id):
    dish = Dish.objects.get(pk=dish_id) # select_related?
    if request.method == 'POST': # If the form has been submitted...
        form = DishMultiplyForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            factor = form.cleaned_data['factor']
            operation = form.cleaned_data['operation']
            if operation == u'multiply':
                dish.quantity = dish.quantity * factor
            else:
                dish.quantity = dish.quantity / factor
            dish.save()
            for amount in dish.contained_comestibles_set.all():
                if operation == u'multiply':
                    amount.quantity = amount.quantity * factor
                else:
                    amount.quantity = amount.quantity / factor
                amount.save()
            return redirect('dish_detail', dish.id) # Redirect after POST
    else:
        form = DishMultiplyForm() # An unbound form
#        print >> sys.stderr, form

    return render_to_response('food/dish_multiply.html', {
        'form': form,
        'dish': dish,},
        context_instance=RequestContext(request) # needed for csrf token
    )

class DishDuplicateForm(forms.Form):
    # form for entry of date for new instance of the dish
    date = forms.DateField(initial=datetime.date.today, label='Cook this dish again on')

def dish_duplicate(request, dish_id):
    # create copy of dish with same amounts, cooked on the given date
    old_dish = Dish.objects.get(pk=dish_id) # select_related?
    if request.method == 'POST': # If the form has been submitted...
        form = DishDuplicateForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            date = form.cleaned_data['date']
            # Create a new instance of the old dish using the given date
            new_dish = old_dish.clone()
            new_dish.date_cooked = date
            new_dish.save()
            for old_amount in old_dish.contained_comestibles_set.all():
                new_amount = old_amount.clone()
                new_amount.containing_dish = new_dish
                new_amount.save()
            return redirect('dish_detail', new_dish.id) # Redirect after POST
    else:
        form = DishDuplicateForm() # An unbound form
#        print >> sys.stderr, form

    return render_to_response('food/dish_duplicate.html', {
        'form': form,
        'dish': old_dish,},
        context_instance=RequestContext(request) # needed for csrf token
    )

class MealDuplicateForm(forms.Form):
    # form for entry of date for new instance of the meal
    date = forms.DateField(initial=datetime.date.today, label='Eat this meal again on')
    # also get new name? e.g. for lunch as dinner
    # and another user? would make it easier to create the same meal for more
    # than one user

def meal_duplicate(request, meal_id):
    # Creates a copy of meal with same portions, eaten on the given date.

    # This creates new portions of the original dish, which shouldn't be
    # allowed in general - if portion.comestible.is_dish, then it should ask
    # whether to use an existing portion or create a new one, if the dish still
    # has a remaining quantity, or whether to cook the dish again
    old_meal = Meal.objects.get(pk=meal_id) # select_related?
    if request.method == 'POST': # If the form has been submitted...
        form = MealDuplicateForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            date = form.cleaned_data['date']
            # Create a new instance of the old meal using the given date
            new_meal = old_meal.clone()
            new_meal.date = date
            new_meal.save()
            for old_portion in old_meal.portion_set.all(): # use meal.comestibles?
                new_portion = old_portion.clone()
                new_portion.meal = new_meal
                new_portion.save()
            return redirect('meal_detail', new_meal.id) # Redirect after POST
    else:
        form = MealDuplicateForm() # An unbound form
#        print >> sys.stderr, form

    return render_to_response('food/meal_duplicate.html', {
        'form': form,
        'meal': old_meal,},
        context_instance=RequestContext(request) # needed for csrf token
    )


def get_sum_day_calories(day):
    """
    Return the total calories in all meals on a date
    """
    # FIXME poor little database sobs in the corner
    # This should use an existing queryset instead
    meals = Meal.objects.filter(date=day)
    return sum(meal.calories for meal in meals)

def get_avg_week_calories(week_start_date):
    """
    Return the daily average calories over a week (only counting days with calories > 0)
    """
    total_calories = 0
    day = week_start_date
    day_count = 0
    while day < (week_start_date + datetime.timedelta(weeks=1)):
        # FIXME this queries the database many times more than necessary
        day_calories = get_sum_day_calories(day)
        if day_calories != 0: # could check if any meals exist instead...
            total_calories += day_calories
            day_count += 1
        day += datetime.timedelta(days=1)
    if day_count:
        return total_calories / day_count
    else:
        return 0

def get_week_starts_in_month(month_start_date):
    """
    Return a list of datetime objects representing the first day of every
    week containing a day of the month, given the month_start_date
    """
    week_start = month_start_date - datetime.timedelta(month_start_date.weekday())
    # Could use _month_bounds() (from dates generic views) here instead
    if month_start_date.month == 12:
        next_month_start_date = month_start_date.replace(
            year=month_start_date.year + 1, month=1)
    else:
        next_month_start_date = month_start_date.replace(
            month=month_start_date.month + 1)
    week_date_list = []
    while week_start < next_month_start_date:
        week_date_list.append(week_start)
        week_start += datetime.timedelta(weeks=1)
    return week_date_list

class MealMonthArchiveView(MonthArchiveView):

    model = Meal
    date_field = "date"
    allow_future = True
    month_format = '%m'

    def get_context_data(self, **kwargs):

        # Call the base implementation first to get a context
        context = super(MealMonthArchiveView, self).get_context_data(**kwargs)

        # Add in week list: a list of dictionaries with date and calories keys
        month_start_date = self.get_dated_items()[2]['month']
        week_start_list = get_week_starts_in_month(month_start_date)

        # Only need to get date_list here to sort it
        # (it's in reverse order by default)
        queryset = self.get_dated_items()[1]
        date_list = self.get_date_list(queryset, 'day')
        date_list.sort() # into chronological order

        context.update({
            'week_list':
                [{'date' : date,
                  'calories': get_avg_week_calories(date)}
                      for date in week_start_list],
            'date_list': date_list,
        })
        return context

class MealWeekArchiveView(WeekArchiveView):

    model = Meal
    date_field = "date"
    allow_future = True
    week_format = '%W'

    def get_next_week(self, date):
        """
        Get the next valid week.
        """
        first_day, last_day = _week_bounds(date)
        next = (last_day + datetime.timedelta(days=1))
        first_day_with_meal = _get_next_prev_month(
            self,
            next,
            is_previous=False,
            # use_first_day makes the result the first day of a month
            use_first_day=False)
        if first_day_with_meal:
            # _get_next_prev_month can't get the first day of a week,
            # so have to use _week_bounds again to do that
            next_week = _week_bounds(first_day_with_meal)[0]
            return next_week

    def get_previous_week(self, date):
        """
        Get the previous valid week.
        """
#        print >> sys.stderr, "Date: ", date
        first_day, last_day = _week_bounds(date)
#        print >> sys.stderr, "First day ", first_day, "; last day:", last_day
        # prev is actually the last day of the previous week:
        prev = (first_day - datetime.timedelta(days=1))
#        print >> sys.stderr, "Prev: ", prev
        first_day_with_meal = _get_next_prev_month(
            self,
            prev,
            is_previous=True,
            # use_first_day makes the result the first day of a month
            use_first_day=False)
        if first_day_with_meal:
            # _get_next_prev_month can't get the first day of a week,
            # so have to use _week_bounds again to do that
            previous_week = _week_bounds(first_day_with_meal)[0]
#            print >> sys.stderr, "Previous week: ", previous_week
            return previous_week

    def get_context_data(self, **kwargs):

        # Call the base implementation first to get a context
        context = super(MealWeekArchiveView, self).get_context_data(**kwargs)

        # Add in calories avg for the week, date list, next and previous weeks
        week_start_date = self.get_dated_items()[2]['week']

        queryset = self.get_dated_items()[1]
        date_list = self.get_date_list(queryset, 'day')
        date_list.sort() # into chronological order

        context.update({
            'avg_week_calories': get_avg_week_calories(week_start_date),
            'date_list': date_list,
            'next_week': self.get_next_week(week_start_date),
            'previous_week': self.get_previous_week(week_start_date),
        })
        return context

class MealDayArchiveView(DayArchiveView):

    model = Meal
    date_field = "date"
    allow_future = True
    month_format = '%m'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(MealDayArchiveView, self).get_context_data(**kwargs)
        # Add in calories sum for the day
        day = self.get_dated_items()[2]['day']
        context['day_calories'] = get_sum_day_calories(day)
        return context


def _week_bounds(date):
    """
    Helper: return the first and last days of the week for the given date.
    """
    first_day = date - datetime.timedelta(date.weekday())
    # _month_bounds actually returns the first day of the next month
    # for 'last_month', but I am going to try to do what it says it should
    last_day = first_day + datetime.timedelta(days=6)
    return first_day, last_day


# This is copied directly from django/views/generic/dates.py, since it
# can't be imported;
# Probably a really bad idea to do this....
def _get_next_prev_month(
        generic_view,
        naive_result,
        is_previous,
        use_first_day):
    """
    Helper: Get the next or the previous valid date. The idea is to allow
    links on month/day views to never be 404s by never providing a date
    that'll be invalid for the given view.

    This is a bit complicated since it handles both next and previous months
    and days (for MonthArchiveView and DayArchiveView); hence the coupling to
    generic_view.

    However in essence the logic comes down to:

        * If allow_empty and allow_future are both true, this is easy: just
          return the naive result (just the next/previous day or month,
          reguardless of object existence.)

        * If allow_empty is true, allow_future is false, and the naive month
          isn't in the future, then return it; otherwise return None.

        * If allow_empty is false and allow_future is true, return the next
          date *that contains a valid object*, even if it's in the future. If
          there are no next objects, return None.

        * If allow_empty is false and allow_future is false, return the next
          date that contains a valid object. If that date is in the future, or
          if there are no next objects, return None.

    """
    date_field = generic_view.get_date_field()
    allow_empty = generic_view.get_allow_empty()
    allow_future = generic_view.get_allow_future()

    # If allow_empty is True the naive value will be valid
    if allow_empty:
        result = naive_result

    # Otherwise, we'll need to go to the database to look for an object
    # whose date_field is at least (greater than/less than) the given
    # naive result
    else:
        # Construct a lookup and an ordering depending on whether we're doing
        # a previous date or a next date lookup.
        if is_previous:
            lookup = {'%s__lte' % date_field: naive_result}
            ordering = '-%s' % date_field
#            print >> sys.stderr, "Lookup: ", lookup ##########################
        else:
            lookup = {'%s__gte' % date_field: naive_result}
            ordering = date_field

        qs = generic_view.get_queryset().filter(**lookup).order_by(ordering)

        # Snag the first object from the queryset; if it doesn't exist that
        # means there's no next/previous link available.
        try:
            result = getattr(qs[0], date_field)
#            print >> sys.stderr, "Result: ", result ##########################
        except IndexError:
            result = None

    # Convert datetimes to a dates
    if hasattr(result, 'date'):
        result = result.date()

    # For month views, we always want to have a date that's the first of the
    # month for consistency's sake.
    if result and use_first_day:
        result = result.replace(day=1)

    # Check against future dates.
    if result and (allow_future or result < datetime.date.today()):
        return result
    else:
        return None

