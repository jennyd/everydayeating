from django.shortcuts import HttpResponse, HttpResponseRedirect, render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import Http404
# from django.views.generic import list_detail # old function-based generic views
# from django.views.generic import  # new class-based generic views
from django.forms.models import modelformset_factory, inlineformset_factory
from food.models import Ingredient, Dish, Amount

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


def dish_edit_amounts(request, dish_id):
    DishFormSet = inlineformset_factory(Dish, Amount, fk_name="containing_dish")
    dish = Dish.objects.get(pk=dish_id)
    if request.method == 'POST':
        formset = DishFormSet(request.POST, request.FILES, instance=dish)
        if formset.is_valid():
            formset.save()
            return HttpResponseRedirect('/food/dishes/')
    else:
        formset = DishFormSet(instance=dish)
    return render_to_response("food/dish_edit_amounts.html", {
        "formset": formset,},
        context_instance=RequestContext(request) # needed for csrf token
    )





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

