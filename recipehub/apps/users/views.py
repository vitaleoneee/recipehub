from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.views.generic.edit import UpdateView

User = get_user_model()


def profile(request):
    return render(request, "account/profile.html")


class ProfileUpdateView(UpdateView):
    model = User
    fields = ["username", "email", "date_of_birth", "photo"]
    template_name = "account/profile_edit.html"
    success_url = "/"
