from django.db import transaction
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from recipehub.apps.recipes.api import permissions as recipe_custom_permissions
from recipehub.apps.recipes.api.pagination import CategoryPagination

from recipehub.apps.recipes.api.serializers import RecipeSerializer, CategorySerializer, RecipeModerationSerializer
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

    # Special lists block
    @action(detail=False, methods=["get"], url_path="my-recipes", permission_classes=[IsAuthenticated])
    def my_recipes(self, request):
        recipes = Recipe.objects.filter(user=self.request.user)
        serializer = RecipeSerializer(recipes, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Moderation block
    @action(detail=False, methods=["get"], url_path="in-process",
            name="Recipes are being moderated",
            permission_classes=[IsAdminUser])
    def get_in_process_recipes(self, request):
        recipes = Recipe.objects.filter(moderation_status="in_process")
        serializer = RecipeSerializer(recipes, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["patch"], url_path="moderate", name="Moderate recipe",
            permission_classes=[IsAdminUser])
    def moderate(self, request, slug=None):
        recipe = self.get_object()

        serializer = RecipeModerationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_recipe_status = serializer.validated_data["status"]

        with transaction.atomic():
            recipe.moderation_status = new_recipe_status
            recipe.save(update_fields=["moderation_status"])

        return Response({
            "id": recipe.id,
            "slug": recipe.slug,
            "status": new_recipe_status,
        }, status=status.HTTP_200_OK
        )
