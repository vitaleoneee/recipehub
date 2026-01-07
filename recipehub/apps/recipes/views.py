from django.shortcuts import render
from django.views.generic import ListView

from recipehub.apps.recipes.models import Recipe


def index(request):
    return render(request, "recipes/index.html", context={"home_active": True})


class RecipesList(ListView):
    model = Recipe
    context_object_name = "recipes"
    paginate_by = 2

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["list_active"] = True
        return context


def recipe_detail(request, slug):
    recipe = Recipe.objects.get(slug=slug)
    return render(request, "recipes/recipe_detail.html", {"recipe": recipe})
