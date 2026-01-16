from django.contrib.auth.decorators import login_required
from django.contrib.postgres.search import SearchVector
from django.core.paginator import Paginator
from django.db.models.aggregates import Avg
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView

from recipehub.apps.recipes.decorators import require_post_json
from recipehub.apps.recipes.forms import RecipeForm
from recipehub.apps.recipes.models import Recipe
from recipehub.apps.reviews.models import Review, Comment
from recipehub.apps.users.models import UserRecipeFavorite
from recipehub.redis import r


def index(request):
    return render(request, "recipes/index.html", context={"home_active": True})


class RecipesList(ListView):
    model = Recipe
    context_object_name = "recipes"
    paginate_by = 2

    def get_queryset(self):
        search_query = self.request.GET.get("search", "")
        if search_query:
            return Recipe.objects.annotate(
                search=SearchVector("name")
                + SearchVector("ingredients")
                + SearchVector("recipe_text")
            ).filter(search=search_query)
        return Recipe.objects.filter(moderation_status="approved")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_query = self.request.GET.get("search", "")
        if search_query:
            context["page_header"] = f"Recipes according to your query: {search_query}"
        else:
            context["page_header"] = "All Recipes"
        context["list_active"] = True
        return context

    def paginate_queryset(self, queryset, page_size):
        paginator = Paginator(queryset, page_size)
        page = self.request.GET.get("page")
        page_obj = paginator.get_page(page)

        return paginator, page_obj, page_obj.object_list, page_obj.has_other_pages()


@login_required
def recipe_detail(request, slug):
    recipe = get_object_or_404(Recipe, slug=slug, moderation_status="approved")
    average_rating = Review.objects.filter(recipe=recipe).aggregate(Avg("rating"))[
        "rating__avg"
    ]
    redis_user_recipe_view_key = f"user:{request.user.id}:recipe:{recipe.id}:view"
    redis_all_recipe_view_key = f"recipe:{recipe.id}:views"

    if not r.exists(redis_user_recipe_view_key):
        r.set(redis_user_recipe_view_key, 1)
        r.incr(redis_all_recipe_view_key)
    is_favorited = UserRecipeFavorite.objects.filter(
        user=request.user, recipe=recipe
    ).exists()
    comments = Comment.objects.filter(recipe=recipe)

    if request.method == "POST":
        body = request.POST.get("body", "").strip()
        if body:
            Comment.objects.create(user=request.user, recipe=recipe, body=body)
            return redirect("recipes:recipe-detail", slug=slug)

    paginator = Paginator(comments, 5)
    page_number = request.GET.get("page")
    comments_page = paginator.get_page(page_number)

    recipe_views = int(r.get(redis_all_recipe_view_key) or 0)

    return render(
        request,
        "recipes/recipe_detail.html",
        {
            "recipe": recipe,
            "average_rating": average_rating,
            "is_favorited": is_favorited,
            "comments": comments_page,
            "views": recipe_views,
        },
    )


@login_required
def add_recipe(request):
    if request.method == "POST":
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.user = request.user
            recipe.save()
            return redirect("recipes:index")
    else:
        form = RecipeForm()
    return render(
        request,
        "recipes/recipe_add.html",
        context={"add_recipe_active": True, "form": form},
    )


@login_required
@require_post_json
def save_recipe(request):
    data = request.json_data

    slug = data.get("slug")
    if not slug:
        return JsonResponse({"error": "Missing fields"}, status=400)

    recipe = get_object_or_404(Recipe, slug=slug)

    favorite, created = UserRecipeFavorite.objects.get_or_create(
        user=request.user, recipe=recipe
    )

    if not created:
        favorite.delete()
        new_status = False
    else:
        new_status = True

    return JsonResponse(
        {
            "status": "ok",
            "is_favorited": new_status,
        }
    )
