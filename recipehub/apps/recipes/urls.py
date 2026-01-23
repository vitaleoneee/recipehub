from django.urls import path

from recipehub.apps.recipes import views

app_name = "recipes"
urlpatterns = [
    path("", views.index, name="index"),
    path("recipes/", views.RecipesList.as_view(), name="recipes-list"),
    path("recipes/add", views.add_recipe, name="recipe-add"),
    path("recipes/<slug:slug>", views.recipe_detail, name="recipe-detail"),
    path("save-recipe/", views.save_recipe, name="save-recipe"),
    path("recipe-builder/", views.recipe_builder, name="recipe-builder"),
]
