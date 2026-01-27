from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from recipehub.apps.recipes.api.views import RecipeViewSet, CategoryViewSet
from recipehub.apps.users.api.views import UserViewSet

router = DefaultRouter()
router.register("recipes", RecipeViewSet)
router.register("categories", CategoryViewSet)
router.register("users", UserViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("recipehub.apps.recipes.urls")),
    path("accounts/", include("recipehub.apps.users.urls")),
    path("reviews/", include("recipehub.apps.reviews.urls")),
    path("api/", include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
