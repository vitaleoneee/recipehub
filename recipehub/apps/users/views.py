import json
from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.views.generic.edit import UpdateView
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from recipehub.apps.users.models import UserRecipeFavorite

from recipehub.apps.recipes.models import Recipe

User = get_user_model()


def profile(request):
    pending_recipes = Recipe.objects.filter(user=request.user, approved=False)
    return render(
        request, "account/profile.html", context={"pending_recipes": pending_recipes}
    )


class ProfileUpdateView(UpdateView):
    model = User
    fields = ["username", "email", "date_of_birth", "photo"]
    template_name = "account/profile_edit.html"
    success_url = "/"


def saved_recipes(request):
    saved = UserRecipeFavorite.objects.filter(user=request.user)
    return render(request, "users/saved_recipes.html", context={"saved_recipes": saved})


@login_required
def remove_saved_recipe(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    slug = data.get("slug")
    if not slug:
        return JsonResponse({"error": "Missing 'slug' field"}, status=400)

    recipe = get_object_or_404(Recipe, slug=slug)

    favorite = UserRecipeFavorite.objects.filter(user=request.user, recipe=recipe)
    if favorite.exists():
        favorite.delete()
        return JsonResponse({"status": "ok", "removed": True})
    else:
        return JsonResponse(
            {"status": "ok", "removed": False, "message": "Recipe was not in favorites"}
        )
