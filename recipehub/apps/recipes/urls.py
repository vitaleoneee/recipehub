from django.urls import path

from recipehub.apps.recipes.views import index

app_name = "recipes"
urlpatterns = [
    path("", index, name="index"),
]
