from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from recipehub.apps.recipes.api.views import RecipeViewSet, CategoryViewSet
from recipehub.apps.reviews.api.views import ReviewViewSet, CommentViewSet
from recipehub.apps.users.api.views import UserViewSet

router = DefaultRouter()
router.register("recipes", RecipeViewSet)
router.register("categories", CategoryViewSet)
router.register("users", UserViewSet)
router.register("reviews", ReviewViewSet)
router.register("comments", CommentViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("recipehub.apps.recipes.urls")),
    path("accounts/", include("recipehub.apps.users.urls")),
    path("reviews/", include("recipehub.apps.reviews.urls")),
    path("api/", include(router.urls)),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
