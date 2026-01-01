from django.urls import path, include

from recipehub.apps.users import views

urlpatterns = [
    path("", include("allauth.urls")),
    path("profile/", views.profile, name="profile"),
]
