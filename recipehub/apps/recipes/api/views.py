from django.db.models import Q

import recipehub.api_permissions as custom_permissions
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from recipehub.apps.recipes.api.pagination import CategoryPagination

from recipehub.apps.recipes.api.serializers import (
    RecipeSerializer,
    CategorySerializer,
    RecipeModerationSerializer,
    UserRecipeFavoriteSerializer,
)
from recipehub.apps.recipes.models import Recipe, Category
from recipehub.apps.recipes.utils import get_best_recipes
from recipehub.apps.users.models import UserRecipeFavorite


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = CategoryPagination

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), permissions.IsAdminUser()]


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    lookup_field = "slug"
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = {
        "category__name": ["exact"],
        "cooking_time": ["exact", "gt", "gte", "lt", "lte"],
    }
    search_fields = ["name", "ingredients", "recipe_text"]
    ordering_fields = ["name", "cooking_time", "created_at"]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Recipe.objects.all()
        return Recipe.objects.filter(moderation_status="approved")

    def get_permissions(self):
        if self.action in ["list"]:
            return [permissions.AllowAny()]
        elif self.action in ["create", "retrieve"]:
            return [permissions.IsAuthenticated()]
        elif self.action == "destroy":
            return [
                permissions.IsAuthenticated(),
                custom_permissions.IsAdminOrOwner(),
            ]
        elif self.action in ["update", "partial_update", "destroy"]:
            return [
                permissions.IsAuthenticated(),
                custom_permissions.IsAdminOrOwner(),
            ]
        return [permissions.IsAuthenticated()]

    # Special lists block
    @action(
        detail=False,
        methods=["get"],
        url_path="my-recipes",
        permission_classes=[IsAuthenticated],
    )
    def my_recipes(self, request):
        recipes = self.get_queryset().filter(user=self.request.user)
        serializer = RecipeSerializer(recipes, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=["get"],
        url_path="best-recipes",
        name="Best recipes",
        permission_classes=[IsAuthenticated],
    )
    def get_best_recipes(self, request):
        best_recipes = get_best_recipes()
        serializer = RecipeSerializer(
            best_recipes, many=True, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Moderation block
    @action(
        detail=False,
        methods=["get"],
        url_path="in-process",
        name="Recipes are being moderated",
        permission_classes=[IsAuthenticated, IsAdminUser],
    )
    def get_in_process_recipes(self, request):
        recipes = Recipe.objects.filter(moderation_status="in_process")
        serializer = RecipeSerializer(recipes, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["patch"],
        url_path="moderate",
        name="Moderate recipe",
        permission_classes=[IsAuthenticated, IsAdminUser],
    )
    def moderate(self, request, slug=None):
        recipe = self.get_object()

        serializer = RecipeModerationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_recipe_status = serializer.validated_data["status"]

        with transaction.atomic():
            recipe.moderation_status = new_recipe_status
            recipe.save(update_fields=["moderation_status"])

        return Response(
            {
                "id": recipe.id,
                "slug": recipe.slug,
                "status": new_recipe_status,
            },
            status=status.HTTP_200_OK,
        )

    # Add and Delete from "Favorites" block
    @action(
        detail=True,
        methods=["post", "delete"],
        url_path="favorite",
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, slug=None):
        recipe = self.get_object()
        user = request.user

        if recipe.user == user:
            return Response(
                {"detail": "You cannot add your recipe to favorites"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        favorite_qs = UserRecipeFavorite.objects.filter(user=user, recipe=recipe)

        if request.method == "POST":
            favorite, created = UserRecipeFavorite.objects.get_or_create(
                user=user, recipe=recipe
            )

            if not created:
                return Response(
                    {"detail": "Recipe already in favorites"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = UserRecipeFavoriteSerializer(
                favorite, context={"request": request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if not favorite_qs.exists():
            return Response(
                {"detail": "Recipe not in favorites"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        favorite_qs.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # Recipe Builder block
    @action(
        detail=False,
        methods=["get"],
        url_path="builder",
        name="Recipe builder",
        permission_classes=[IsAuthenticated],
    )
    def recipe_builder(self, request):
        ingredients = request.query_params.get("ingredients", "").split(",")
        q = Q()
        for ing in ingredients:
            q |= Q(ingredients__icontains=ing)
        queryset = Recipe.objects.select_related("user", "category") \
            .filter(moderation_status="approved") \
            .filter(q)
        serializer = RecipeSerializer(queryset, many=True, context={"request": request})
        return Response({"recipes": serializer.data}, status=status.HTTP_200_OK)
