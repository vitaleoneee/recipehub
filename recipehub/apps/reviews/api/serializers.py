from rest_framework import serializers

from recipehub.apps.reviews.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = ["user", "recipe", "rating", "created_at"]

    read_only_fields = ["created_at"]

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return Review.objects.create(**validated_data)
