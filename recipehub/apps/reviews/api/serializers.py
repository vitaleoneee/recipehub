from django.contrib.auth import get_user_model
from rest_framework import serializers

from recipehub.apps.reviews.models import Review, Comment

User = get_user_model()


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = ["user", "recipe", "rating", "created_at"]

    read_only_fields = ["created_at"]

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return Review.objects.create(**validated_data)

    def validate(self, attrs):
        recipe = attrs["recipe"]
        user = self.context["request"].user

        if recipe.user == user:
            raise serializers.ValidationError("You can't review yourself")
        return attrs


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    active = serializers.BooleanField(read_only=True)

    class Meta:
        model = Comment
        fields = ["user", "recipe", "body", "created_at", "active"]

    read_only_fields = ["created_at"]

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return Comment.objects.create(**validated_data)


class CommentAdminSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=False
    )

    class Meta:
        model = Comment
        fields = ["user", "recipe", "body", "active", "created_at"]

    read_only_fields = ["created_at"]

    def create(self, validated_data):
        request_user = self.context["request"].user

        if not validated_data.get("user"):
            validated_data["user"] = request_user

        return Comment.objects.create(**validated_data)


class CommentStatusSerializer(serializers.Serializer):
    active = serializers.BooleanField()
