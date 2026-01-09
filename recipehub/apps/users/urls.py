from django.urls import path, include

from recipehub.apps.users import views

urlpatterns = [
    path("", include("allauth.urls")),
    path("profile/", views.profile, name="profile"),
    path(
        "profile-edit/<int:pk>", views.ProfileUpdateView.as_view(), name="profile-edit"
    ),
    path("saved-recipes", views.saved_recipes, name="saved-recipes"),
    path("remove-saved-recipe/", views.remove_saved_recipe, name="remove_saved_recipe"),
]
