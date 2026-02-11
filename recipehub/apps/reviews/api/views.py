from rest_framework.request import Request

from django.db import transaction
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
    queryset = Review.objects.all().order_by("pk")
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self) -> list[BasePermission]:
        if self.action == "create":
            return [permissions.IsAuthenticated()]
        elif self.action in ["update_by_recipe", "update", "partial_update", "destroy"]:
            return [
                permissions.IsAuthenticated(),
                custom_permissions.IsAdminOrOwner(),
            ]
        elif self.action == "list":
            # Allow authenticated users to list their own reviews; staff will see all
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]

    def list(self, request, *args, **kwargs):
        # For staff return all reviews, otherwise return only user's reviews
        if request.user.is_staff:
            queryset = self.filter_queryset(self.get_queryset()).order_by("pk")
        else:
            queryset = Review.objects.filter(user=request.user).order_by("pk")

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(
        detail=False, methods=["put", "patch"], url_path=r"recipes/(?P<recipe_id>\d+)"
    )
    def update_by_recipe(
        self, request: Request, recipe_id: int | None = None
    ) -> Response:
        try:
            review = Review.objects.get(recipe_id=recipe_id)
        except Review.DoesNotExist:
            return Response(
                {"detail": "Review not found for this recipe"},
                status=status.HTTP_404_NOT_FOUND,
            )

        self.check_object_permissions(request, review)

        serializer = self.get_serializer(review, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().order_by("pk")
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
        comments = Comment.objects.filter(user=self.request.user).order_by("pk")
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
