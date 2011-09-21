from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404
from food.models import Ingredient


def ingredient_index(request):
    ingredient_list = Ingredient.objects.all().order_by('name')[:10]
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

def ingredient_add(request):
    return HttpResponse("Hello, world. You're trying to add a new ingredient.")

