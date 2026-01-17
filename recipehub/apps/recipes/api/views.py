from rest_framework import viewsets

from recipehub.apps.recipes.api.serializers import RecipeSerializer
from recipehub.apps.recipes.models import Recipe


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
