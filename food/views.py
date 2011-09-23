from django.shortcuts import HttpResponse, HttpResponseRedirect, render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import Http404
from food.models import Ingredient, IngredientForm, Dish, DishForm, Amount, AmountForm


def ingredient_index(request):
    ingredient_list = Ingredient.objects.all().order_by('name')#[:10]
    return render_to_response('food/ingredient_index.html', {'ingredient_list': ingredient_list})

#    t = loader.get_template('food/ingredient_index.html')
#    c = Context({
#        'ingredient_list': ingredient_list,
#    })
#    return HttpResponse(t.render(c))

#    output = ', '.join([i.name for i in ingredient_list])
#    return HttpResponse(output)

#    return HttpResponse("Hello, world. You're at the ingredients index.")


def ingredient_detail(request, ingredient_id):
    i = get_object_or_404(Ingredient, pk=ingredient_id)

#    try:
#        i = Ingredient.objects.get(pk=ingredient_id)
#    except Ingredient.DoesNotExist:
#        raise Http404

    return render_to_response('food/ingredient_detail.html', {'ingredient': i})

#    return HttpResponse("You're looking at ingredient %s." % ingredient_id)


def ingredient_edit(request, ingredient_id):
    i = get_object_or_404(Ingredient, pk=ingredient_id)
    if request.method == 'POST': # If the form has been submitted...
        form = IngredientForm(request.POST, instance=i) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            # ...
            # FIXME Is cleaning also necessary with ModelForm?
            form.save()
            return HttpResponseRedirect('thanks/') # Redirect after POST
    else:
        form = IngredientForm(instance=i) # A bound form
        # FIXME name should not be editable (or if it is, a new ingredient should be added and the old one unedited)

    return render_to_response('food/ingredient_edit.html', {
        'form': form}, context_instance=RequestContext(request)) # render_to_response() wants RequestContext rather than Context (default) for its extra csrf token
        # https://docs.djangoproject.com/en/1.2/ref/templates/api/#django-core-context-processors-csrf

#    return HttpResponse("Hello, world. You're trying to edit %s." % i.name)


def ingredient_add(request):
    if request.method == 'POST': # If the form has been submitted...
        form = IngredientForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            # ...
            # FIXME Is cleaning also necessary with ModelForm?
            form.save()
            return HttpResponseRedirect('thanks/') # Redirect after POST
    else:
        form = IngredientForm() # An unbound form

    return render_to_response('food/ingredient_add.html', {
        'form': form}, context_instance=RequestContext(request)) # render_to_response() wants RequestContext rather than Context (default) for its extra csrf token
        # https://docs.djangoproject.com/en/1.2/ref/templates/api/#django-core-context-processors-csrf


def ingredient_add_thanks(request):
    ingredient_list = Ingredient.objects.all().order_by('name')
    thanks_message = "Thanks for adding a new ingredient!"
    return render_to_response('food/ingredient_thanks.html', {'thanks_message': thanks_message, 'ingredient_list': ingredient_list})

#    return HttpResponse("Thanks for adding a new ingredient!")


def ingredient_edit_thanks(request, ingredient_id):
    ingredient_list = Ingredient.objects.all().order_by('name')
    thanks_message = "Thanks! Ingredient %s has been updated." % ingredient_id
    return render_to_response('food/ingredient_thanks.html', {'thanks_message': thanks_message, 'ingredient_list': ingredient_list})

#    return HttpResponse("Thanks! That ingredient has been updated.")
#    return HttpResponse("Thanks! Ingredient %s has been updated." % ingredient_id) # FIXME would be better to have name here rather than id, but seems daft to have to get it again...


#########################################

def dish_index(request):
    dish_list = Dish.objects.all().order_by('date_cooked')#[:10]
    return render_to_response('food/dish_index.html', {'dish_list': dish_list})


def dish_detail(request, dish_id):
    d = get_object_or_404(Dish, pk=dish_id)
    # get amounts for this dish and return them
    amounts = Amount.objects.filter(containing_dish=dish_id)    
    return render_to_response('food/dish_detail.html', {'dish': d, 'amounts': amounts})


def dish_edit(request, dish_id):
    d = get_object_or_404(Dish, pk=dish_id)
    if request.method == 'POST': # If the form has been submitted...
        form = DishForm(request.POST, instance=d) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            # ...
            # FIXME Is cleaning also necessary with ModelForm?
            form.save()
            return HttpResponseRedirect('thanks/') # Redirect after POST
    else:
        form = DishForm(instance=d) # A bound form
        # FIXME name should not be editable (or if it is, a new ingredient should be added and the old one unedited)

    return render_to_response('food/dish_edit.html', {
        'form': form}, context_instance=RequestContext(request))










