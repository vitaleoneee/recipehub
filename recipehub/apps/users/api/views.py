from django.contrib.auth import get_user_model
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from recipehub.apps.recipes.api.serializers import RecipeSerializer
from recipehub.apps.recipes.models import Recipe
from recipehub.apps.users.api.serializers import UserSerializer

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("pk")
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

    @action(
        detail=False,
        methods=["get", "put", "patch"],
        url_path="me",
        permission_classes=[IsAuthenticated],
    )
    def me(self, request: Request) -> Response:
        if request.method == "GET":
            serializer = UserSerializer(instance=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif request.method == "PATCH":
            serializer = UserSerializer(
                instance=request.user, data=request.data, partial=True
            )
        else:
            serializer = UserSerializer(instance=request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["get"],
        url_path="recipes",
        permission_classes=[IsAuthenticated],
    )
    def recipes(self, request: Request, *args, **kwargs) -> Response:
        user = self.get_object()

        queryset = (
            Recipe.objects.filter(user=user)
            .select_related("category", "user")
            .order_by("pk", "moderation_status")
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = RecipeSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = RecipeSerializer(queryset, many=True)
        return Response(serializer.data)
