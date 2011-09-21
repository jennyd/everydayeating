from django.shortcuts import HttpResponse, HttpResponseRedirect, render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import Http404
from food.models import Ingredient, IngredientForm


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
    return HttpResponse("Hello, world. You're trying to edit %s." % i.name)


def ingredient_add(request):
    if request.method == 'POST': # If the form has been submitted...
        form = IngredientForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            # ...
            # Is cleaning also necessary with ModelForm?
            form.save()
            return HttpResponseRedirect('thanks/') # Redirect after POST
    else:
        form = IngredientForm() # An unbound form

    return render_to_response('food/ingredient_add.html', {
        'form': form}, context_instance=RequestContext(request)) # render_to_response() wants RequestContext rather than Context (default) for its extra csrf token
        # https://docs.djangoproject.com/en/1.2/ref/templates/api/#django-core-context-processors-csrf


def ingredient_add_thanks(request):
    return HttpResponse("Thanks for adding a new ingredient!")

