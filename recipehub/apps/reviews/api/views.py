from rest_framework import viewsets

from recipehub.apps.reviews.api.serializers import ReviewSerializer
from recipehub.apps.reviews.models import Review


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
