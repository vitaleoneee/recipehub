from django.urls import path, include

from recipehub.apps.users import views

urlpatterns = [
    path("", include("allauth.urls")),
    path("profile/", views.profile, name="profile"),
    path(
        "profile-edit/<int:pk>", views.ProfileUpdateView.as_view(), name="profile-edit"
    ),
]
