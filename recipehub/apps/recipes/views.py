from django.contrib.auth.decorators import login_required
from django.db.models.aggregates import Avg
from django.shortcuts import render, redirect
from django.views.generic import ListView

from recipehub.apps.recipes.forms import RecipeForm
from recipehub.apps.recipes.models import Recipe
from recipehub.apps.reviews.models import Review


def index(request):
    return render(request, "recipes/index.html", context={"home_active": True})


class RecipesList(ListView):
    model = Recipe
    context_object_name = "recipes"
    paginate_by = 2

    def get_queryset(self):
        return Recipe.objects.filter(approved=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["list_active"] = True
        return context


@login_required
def recipe_detail(request, slug):
    recipe = Recipe.objects.get(slug=slug)
    average_rating = Review.objects.filter(recipe=recipe).aggregate(Avg("rating"))[
        "rating__avg"
    ]
    return render(
        request,
        "recipes/recipe_detail.html",
        {"recipe": recipe, "average_rating": average_rating},
    )


@login_required
def add_recipe(request):
    if request.method == "POST":
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.user = request.user
            recipe.save()
            return redirect('recipes:index')
    else:
        form = RecipeForm()
    return render(request, 'recipes/recipe_add.html', context={"add_recipe_active": True, "form": form})
