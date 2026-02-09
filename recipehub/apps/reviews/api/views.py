from urllib.request import Request

from django.db import transaction
from django.db.models import QuerySet
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser, BasePermission
from rest_framework.response import Response

import recipehub.api_permissions as custom_permissions
from recipehub.apps.reviews.api.serializers import (
    ReviewSerializer,
    CommentSerializer,
    CommentStatusSerializer,
    CommentAdminSerializer,
)
from recipehub.apps.reviews.models import Review, Comment


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self) -> QuerySet[Review]:
        user = self.request.user
        if user.is_staff:
            return Review.objects.all()
        return Review.objects.filter(user=user)

    def get_permissions(self) -> list[BasePermission]:
        if self.action == "create":
            return [permissions.IsAuthenticated()]
        elif self.action in ["update", "partial_update", "destroy"]:
            return [
                permissions.IsAuthenticated(),
                custom_permissions.IsAdminOrOwner(),
            ]
        elif self.action == "list":
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get_serializer_class(self) -> type[CommentSerializer | CommentAdminSerializer]:
        if self.request.user.is_staff:
            return CommentAdminSerializer
        return CommentSerializer

    def get_permissions(self) -> list[BasePermission]:
        # For custom actions use permissions from the decorator
        if self.action not in [
            "list",
            "retrieve",
            "create",
            "update",
            "partial_update",
            "destroy",
        ]:
            return super().get_permissions()
        if self.action == "create":
            return [permissions.IsAuthenticated()]
        elif self.action in ["update", "partial_update", "destroy"]:
            return [
                permissions.IsAuthenticated(),
                custom_permissions.IsAdminOrOwner(),
            ]
        elif self.action == "list":
            return [permissions.IsAuthenticated(), permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    @action(
        detail=False,
        methods=["get"],
        url_path="my-comments",
        permission_classes=[IsAuthenticated],
    )
    def my_comments(self, request: Request) -> Response:
        comments = Comment.objects.filter(user=self.request.user)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["patch"],
        url_path="activate",
        name="Set activate comment",
        permission_classes=[IsAuthenticated, IsAdminUser],
    )
    def activate(self, request: Request, *args, **kwargs) -> Response:
        comment = self.get_object()

        serializer = CommentStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_comment_status = serializer.validated_data["active"]

        with transaction.atomic():
            comment.active = new_comment_status
            comment.save(update_fields=["active"])

        return Response(
            {
                "id": comment.id,
                "recipe": comment.recipe_id,
                "active": comment.active,
            },
            status=status.HTTP_200_OK,
        )
