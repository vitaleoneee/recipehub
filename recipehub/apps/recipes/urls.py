from django.urls import path

from recipehub.apps.recipes import views

app_name = "recipes"
urlpatterns = [
    path("", views.index, name="index"),
]
