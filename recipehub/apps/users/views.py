from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.views.generic.edit import UpdateView

from recipehub.apps.recipes.models import Recipe

User = get_user_model()


def profile(request):
    pending_recipes = Recipe.objects.filter(user=request.user, approved=False)
    return render(request, "account/profile.html", context={"pending_recipes": pending_recipes})


class ProfileUpdateView(UpdateView):
    model = User
    fields = ["username", "email", "date_of_birth", "photo"]
    template_name = "account/profile_edit.html"
    success_url = "/"
