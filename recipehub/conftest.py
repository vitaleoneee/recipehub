from io import BytesIO

import fakeredis
import pytest
from PIL import Image
from recipehub.factories import CommentFactory
from django.core.files.uploadedfile import SimpleUploadedFile

from rest_framework.test import APIClient, APIRequestFactory

from recipehub.factories import CategoryFactory, RecipeFactory

from recipehub.factories import UserFactory
import recipehub.redis as redis_module


@pytest.fixture
def valid_signup_data():
    """
    Basic valid data for registration
    """
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password1": "SecurePass123!",
        "password2": "SecurePass123!",
    }


@pytest.fixture
def sample_image():
    """
    Creates a test image
    """
    image = Image.new("RGB", (100, 100), color="red")
    image_io = BytesIO()
    image.save(image_io, format="JPEG")
    image_io.seek(0)
    return SimpleUploadedFile(
        "test_photo.jpg", image_io.read(), content_type="image/jpeg"
    )


@pytest.fixture()
def fake_redis(monkeypatch):
    """
    Fixture for creating a fake redis
    """
    fake_client = fakeredis.FakeStrictRedis()
    monkeypatch.setattr(redis_module, "r", fake_client)
    return fake_client


@pytest.fixture()
def users_list():
    return {
        "recipe_owner_user": UserFactory.create(),
        "first_simple_user": UserFactory.create(),
        "second_simple_user": UserFactory.create(),
        "admin_user": UserFactory.create(),
    }


@pytest.fixture()
def api_client():
    return APIClient()


@pytest.fixture
def api_rf():
    return APIRequestFactory()


@pytest.fixture()
def authenticated_client(users_list):
    client = APIClient()
    user = users_list["first_simple_user"]
    client.force_authenticate(user=user)
    return client


@pytest.fixture()
def admin_client(api_client, users_list):
    user = users_list["admin_user"]
    user.is_staff = True
    user.save()
    api_client.force_authenticate(user=user)
    return api_client


# Recipe fixtures
@pytest.fixture
def recipe_owner(users_list):
    return users_list["recipe_owner_user"]


@pytest.fixture
def recipe_owner_client(recipe_owner):
    client = APIClient()
    client.force_authenticate(user=recipe_owner)
    return client


@pytest.fixture
def recipe(recipe_owner):
    return RecipeFactory(user=recipe_owner, moderation_status="approved")


@pytest.fixture
def recipe_data(recipe_owner, category):
    return {
        "category": category.id,
        "name": "test",
        "ingredients": "test - 1ks",
        "servings": 5,
    }


@pytest.fixture
def recipe_serializer_data(recipe_owner, category):
    return {
        "user": recipe_owner.id,
        "category": category.id,
        "name": "test",
        "slug": "123",
        "ingredients": "test - 1ks",
        "servings": 5,
        "announcement_text": "test",
        "recipe_text": "test",
        "moderation_status": "approved",
        "created_at": "2026-01-02",
    }


@pytest.fixture()
def recipes():
    approved_recipes = RecipeFactory.create_batch(2, moderation_status="approved")
    in_process_recipes = RecipeFactory.create_batch(2, moderation_status="in_process")
    rejected_recipes = RecipeFactory.create_batch(2, moderation_status="rejected")
    return {
        "approved_recipes": approved_recipes,
        "in_process_recipes": in_process_recipes,
        "all_recipes_len": len(approved_recipes)
        + len(in_process_recipes)
        + len(rejected_recipes),
    }


# Category fixtures
@pytest.fixture()
def category():
    return CategoryFactory()


@pytest.fixture()
def category_data():
    return {"name": "test"}


# Comment fixtures
@pytest.fixture
def comment_data(recipe):
    return {
        "recipe": recipe.id,
        "body": "This is a test comment",
    }


@pytest.fixture
def comment_serializer_data(recipe):
    return {
        "recipe": recipe.id,
        "body": "This is a test comment",
    }


@pytest.fixture
def comment(users_list):
    user = users_list["second_simple_user"]
    recipe = RecipeFactory(user=user, moderation_status="approved")
    return CommentFactory(user=user, recipe=recipe)


@pytest.fixture
def comment_owner_client(comment):
    """Client authenticated as comment owner"""
    client = APIClient()
    client.force_authenticate(user=comment.user)
    return client


@pytest.fixture
def comments_fixture(authenticated_client, users_list):
    """Create multiple comments for testing"""
    user1 = users_list["first_simple_user"]
    user2 = users_list["second_simple_user"]

    recipe1 = RecipeFactory(user=user1, moderation_status="approved")
    recipe2 = RecipeFactory(user=user2, moderation_status="approved")

    comments = [
        CommentFactory(user=user1, recipe=recipe1),
        CommentFactory(user=user2, recipe=recipe2),
        CommentFactory(user=user1, recipe=recipe2),
    ]

    return {
        "all_comments": comments,
        "user1_comments": [comments[0], comments[2]],
        "user2_comments": [comments[1]],
    }
