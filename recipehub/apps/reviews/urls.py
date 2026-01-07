from django.urls import path

from recipehub.apps.reviews import views

app_name = "reviews"
urlpatterns = [
    path("send-review/", views.create_review, name="create-review"),
]
