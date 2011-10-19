import datetime, sys

from django.shortcuts import HttpResponse, HttpResponseRedirect, render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.http import Http404
from django.views.generic import MonthArchiveView, WeekArchiveView, DayArchiveView # new class-based generic views
from django.forms.models import modelformset_factory, inlineformset_factory

from food.models import Ingredient, Dish, DishForm, Amount, Meal, MealForm, Eating

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
    DishFormSet = inlineformset_factory(Dish, Amount, fk_name="containing_dish", extra=6) # shouldn't need fk_name any more - only one fk to Dish now
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
            # don't need to save dish again here - signal receivers catch amounts being saved or deleted and update dish for each one
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

def meal_eating_form(request, meal_id=None):
    MealFormSet = inlineformset_factory(Meal, Eating, extra=6)
    if meal_id:
        meal = Meal.objects.get(pk=meal_id)
    else:
        meal = Meal()
    if request.method == 'POST':
        form = MealForm(request.POST, request.FILES, instance=meal)
        formset = MealFormSet(request.POST, request.FILES, instance=meal)
        if form.is_valid() and formset.is_valid():
            # meal can't calculate calories from eatings until they're saved...
            # but eatings need meal to be there first for fk...
            form.save() # do this only if not meal.id? or meal_id?
            formset.save()
            # don't need to save meal again here - signal receivers catch eatings being saved or deleted and update meal for each one
            ## ... so save meal again after eatings are saved from the formset
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

def get_sum_day_calories(day):
    """
    Return the total calories in all meals on a date
    """
    meals = Meal.objects.filter(date=day) # FIXME poor little database sobs in the corner
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
        if day_calories != 0: # could check if there actually are any meals instead...
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

    >>> month_start_date = datetime.datetime(2011, 11, 1, 0, 0)
    >>> get_week_starts_in_month(month_start_date)
    [datetime.datetime(2011, 10, 31, 0, 0),
     datetime.datetime(2011, 11, 7, 0, 0),
     datetime.datetime(2011, 11, 14, 0, 0),
     datetime.datetime(2011, 11, 21, 0, 0),
     datetime.datetime(2011, 11, 28, 0, 0)]

    >>> month_start_date = datetime.datetime(2011, 12, 1, 0, 0)
    >>> get_week_starts_in_month(month_start_date)
    [datetime.datetime(2011, 11, 28, 0, 0),
     datetime.datetime(2011, 12, 5, 0, 0),
     datetime.datetime(2011, 12, 12, 0, 0),
     datetime.datetime(2011, 12, 19, 0, 0),
     datetime.datetime(2011, 12, 26, 0, 0)]

    """
    week_start = month_start_date - datetime.timedelta(month_start_date.weekday())
    # could use _month_bounds() (from dates generic views) or something similar instead here
    if month_start_date.month == 12:
        next_month_start_date = month_start_date.replace(year=month_start_date.year + 1, month=1)
    else:
        next_month_start_date = month_start_date.replace(month=month_start_date.month + 1)
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

        # Only need to get date_list here to sort it (it's in reverse order by default)
        queryset = self.get_dated_items()[1]
        date_list = self.get_date_list(queryset, 'day')
        date_list.sort() # into chronological order

        context.update({
            'week_list': [{'date' : date, 'calories': get_avg_week_calories(date)} for date in week_start_list],
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
        first_day_with_meal = _get_next_prev_month(self, next, is_previous=False, use_first_day=False) # use_first_day makes the result the first day of a month
        if first_day_with_meal:
            next_week = _week_bounds(first_day_with_meal)[0] # _get_next_prev_month can't get the first day of a week, so have to use this to do that
            return next_week

    def get_previous_week(self, date):
        """
        Get the previous valid week.
        """
#        print >> sys.stderr, "Date: ", date
        first_day, last_day = _week_bounds(date)
#        print >> sys.stderr, "First day ", first_day, "; last day:", last_day
        prev = (first_day - datetime.timedelta(days=1)) # this is actually the last day of the previous week
#        print >> sys.stderr, "Prev: ", prev
        first_day_with_meal = _get_next_prev_month(self, prev, is_previous=True, use_first_day=False) # use_first_day makes the result the first day of a month
        if first_day_with_meal:
            previous_week = _week_bounds(first_day_with_meal)[0] # _get_next_prev_month can't get the first day of a week, so have to use this to do that
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
    # _month_bounds actually returns the first day of the next month for 'last_month'
    # but I am going to try to do what it says it should
    last_day = first_day + datetime.timedelta(days=6)
    return first_day, last_day


# This is copied directly from django/views/generic/dates.py, since it can't be imported
# Probably a really bad idea to do this....
def _get_next_prev_month(generic_view, naive_result, is_previous, use_first_day):
    """
    Helper: Get the next or the previous valid date. The idea is to allow
    links on month/day views to never be 404s by never providing a date
    that'll be invalid for the given view.

    This is a bit complicated since it handles both next and previous months
    and days (for MonthArchiveView and DayArchiveView); hence the coupling to generic_view.

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
#            print >> sys.stderr, "Lookup: ", lookup #######################################################
        else:
            lookup = {'%s__gte' % date_field: naive_result}
            ordering = date_field

        qs = generic_view.get_queryset().filter(**lookup).order_by(ordering)

        # Snag the first object from the queryset; if it doesn't exist that
        # means there's no next/previous link available.
        try:
            result = getattr(qs[0], date_field)
#            print >> sys.stderr, "Result: ", result #######################################################
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


#### not used now - generic view for ingredient_list instead
#def ingredient_index(request):
#    ingredient_list = Ingredient.objects.all().order_by('name')#[:10]
#    return render_to_response('food/ingredient_index.html', {'ingredient_list': ingredient_list})

#### previous versions of ingredient_index:
##    t = loader.get_template('food/ingredient_index.html')
##    c = Context({
##        'ingredient_list': ingredient_list,
##    })
##    return HttpResponse(t.render(c))

##    output = ', '.join([i.name for i in ingredient_list])
##    return HttpResponse(output)

##    return HttpResponse("Hello, world. You're at the ingredients index.")


#### not used now - generic view for ingredient_detail instead
#def ingredient_detail(request, ingredient_id):
#    i = get_object_or_404(Ingredient, pk=ingredient_id)

##    try:
##        i = Ingredient.objects.get(pk=ingredient_id)
##    except Ingredient.DoesNotExist:
##        raise Http404

#    return render_to_response('food/ingredient_detail.html', {'ingredient': i})

##    return HttpResponse("You're looking at ingredient %s." % ingredient_id)


#### not used now - generic view for ingredient_edit instead
#def ingredient_edit(request, ingredient_id):
#    i = get_object_or_404(Ingredient, pk=ingredient_id)
#    if request.method == 'POST': # If the form has been submitted...
#        form = IngredientForm(request.POST, instance=i) # A form bound to the POST data
#        if form.is_valid(): # All validation rules pass
#            # Process the data in form.cleaned_data
#            # ...
#            # FIXME Is cleaning also necessary with ModelForm?
#            form.save()
#            return HttpResponseRedirect('thanks/') # Redirect after POST
#    else:
#        form = IngredientForm(instance=i) # A bound form
#        # FIXME name should not be editable (or if it is, a new ingredient should be added and the old one unedited)

#    return render_to_response('food/ingredient_edit.html', {
#        'form': form}, context_instance=RequestContext(request)) # render_to_response() wants RequestContext rather than Context (default) for its extra csrf token
#        # https://docs.djangoproject.com/en/1.2/ref/templates/api/#django-core-context-processors-csrf

##    return HttpResponse("Hello, world. You're trying to edit %s." % i.name)


#### not used now - generic view for ingredient_add instead
#def ingredient_add(request):
#    if request.method == 'POST': # If the form has been submitted...
#        form = IngredientForm(request.POST) # A form bound to the POST data
#        if form.is_valid(): # All validation rules pass
#            # Process the data in form.cleaned_data
#            # ...
#            # FIXME Is cleaning also necessary with ModelForm?
#            form.save()
#            return HttpResponseRedirect('thanks/') # Redirect after POST
#    else:
#        form = IngredientForm() # An unbound form

#    return render_to_response('food/ingredient_add.html', {
#        'form': form}, context_instance=RequestContext(request)) # render_to_response() wants RequestContext rather than Context (default) for its extra csrf token
#        # https://docs.djangoproject.com/en/1.2/ref/templates/api/#django-core-context-processors-csrf


#########################################

#### not used now - much simpler generic view for dish_detail instead
#### template can access dish.contained_amounts_set directly so
#### don't need to put amounts into extra_context
#def dish_detail_with_amounts(request, dish_id):
#    return list_detail.object_detail(
#        request,
#        # queryset = Dish.objects.all(),
#        # this also works, but still requires object_id:
#        queryset = Dish.objects.filter(pk=dish_id), # object_detail filters again on primary key anyway...
#        object_id = dish_id,
#        template_name = "food/dish_detail.html",
#        template_object_name = "dish",
#        extra_context = {"amounts" : Dish.objects.get(pk=dish_id).contained_amounts_set.all()}
#    )

