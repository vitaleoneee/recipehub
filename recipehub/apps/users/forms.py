from django import forms
from allauth.account.forms import SignupForm
from django.http import HttpRequest

from recipehub.apps.users.models import User


class CustomSignupForm(SignupForm):
    date_of_birth = forms.DateField(
        label="Date of Birth (optional)",
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    photo = forms.ImageField(
        label="Photo (optional)", required=False, widget=forms.FileInput
    )

    field_order = [
        "username",
        "password1",
        "password2",
        "email",
        "photo",
        "date_of_birth",
    ]

    def save(self, request: HttpRequest) -> User:
        user = super().save(request)
        user.date_of_birth = self.cleaned_data.get("date_of_birth")
        user.photo = self.cleaned_data.get("photo")
        user.save()
        return user
