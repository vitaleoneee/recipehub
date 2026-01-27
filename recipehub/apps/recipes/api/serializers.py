from rest_framework import serializers

from recipehub.apps.recipes.models import Recipe, Category
from recipehub.apps.recipes.utils import validate_ingredients_format


class CategorySerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="category-detail")

    class Meta:
        model = Category
        fields = ["url", "name", "slug"]
        read_only_fields = ["slug"]


class RecipeSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    category = serializers.HyperlinkedRelatedField(
        view_name="category-detail", queryset=Category.objects.all()
    )

    class Meta:
        model = Recipe
        fields = [
            "user",
            "category",
            "name",
            "slug",
            "announcement_text",
            "photo",
            "ingredients",
            "recipe_text",
            "servings",
            "cooking_time",
            "moderation_status",
            "calories",
            "created_at",
        ]
        read_only_fields = ["user", "created_at", "slug", "moderation_status"]

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return Recipe.objects.create(**validated_data)

    def validate_ingredients(self, value):
        return validate_ingredients_format(value)


class RecipeModerationSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=("approved", "rejected"))
