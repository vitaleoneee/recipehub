from django.shortcuts import render
from django.views.generic import ListView

from recipehub.apps.recipes.models import Recipe


def index(request):
    return render(request, "recipes/index.html")


class RecipesList(ListView):
    model = Recipe
    context_object_name = "recipes"
    paginate_by = 2
