from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("recipehub.apps.recipes.urls")),
    path('accounts/', include('recipehub.apps.users.urls')),
]
