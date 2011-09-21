from django.http import HttpResponse

def ingredient_index(request):
    return HttpResponse("Hello, world. You're at the ingredients index.")

def ingredient_detail(request, ingredient_id):
    return HttpResponse("You're looking at ingredient %s." % ingredient_id)

def ingredient_add(request):
    return HttpResponse("Hello, world. You're trying to add a new ingredient.")

