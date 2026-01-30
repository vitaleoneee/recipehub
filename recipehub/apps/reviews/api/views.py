from rest_framework import viewsets, permissions

from recipehub.apps.reviews.api.serializers import ReviewSerializer
from recipehub.apps.reviews.models import Review


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
