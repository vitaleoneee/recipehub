from rest_framework import viewsets, permissions

from recipehub.apps.recipes.api import permissions as recipe_custom_permissions
from recipehub.apps.recipes.api.pagination import CategoryPagination

from recipehub.apps.recipes.api.serializers import RecipeSerializer, CategorySerializer
from recipehub.apps.recipes.models import Recipe, Category


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = CategoryPagination

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    lookup_field = "slug"

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Recipe.objects.all()
        return Recipe.objects.filter(moderation_status="approved")

    def get_permissions(self):
        if self.action == "create" or self.action == "retrieve":
            return [permissions.IsAuthenticated()]
        elif self.action == "destroy":
            return [recipe_custom_permissions.IsAdminOrOwner()]
        return super().get_permissions()
