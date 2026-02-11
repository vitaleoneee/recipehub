import fakeredis
import pytest
import recipehub.redis as redis_module

from io import BytesIO
from typing import Dict
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile

from rest_framework.test import APIClient, APIRequestFactory

from recipehub.factories import (
    CategoryFactory,
    RecipeFactory,
    CommentFactory,
    ReviewFactory,
    UserFactory,
)

# Constants for moderation statuses
MODERATION_STATUS_APPROVED = "approved"
MODERATION_STATUS_IN_PROCESS = "in_process"
MODERATION_STATUS_REJECTED = "rejected"


@pytest.fixture(autouse=True)
def media_root(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path


@pytest.fixture
def valid_signup_data() -> Dict[str, str]:
    """Basic valid data for user registration."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password1": "SecurePass123!",
        "password2": "SecurePass123!",
    }


@pytest.fixture
def sample_image() -> SimpleUploadedFile:
    """Creates a test image file for testing image uploads."""
    image = Image.new("RGB", (100, 100), color="red")
    image_io = BytesIO()
    image.save(image_io, format="JPEG")
    image_io.seek(0)
    return SimpleUploadedFile(
        "test_photo.jpg", image_io.read(), content_type="image/jpeg"
    )


@pytest.fixture()
def fake_redis(monkeypatch) -> fakeredis.FakeStrictRedis:
    """Provides a fake Redis client for testing without a real Redis instance."""
    fake_client = fakeredis.FakeStrictRedis()
    monkeypatch.setattr(redis_module, "r", fake_client)
    return fake_client


@pytest.fixture()
def users_list() -> Dict[str, object]:
    """Creates a dictionary of test users for various test scenarios."""
    return {
        "recipe_owner_user": UserFactory(),
        "first_simple_user": UserFactory(),
        "second_simple_user": UserFactory(),
        "admin_user": UserFactory(),
    }


@pytest.fixture()
def api_client() -> APIClient:
    """Provides an unauthenticated API client."""
    return APIClient()


@pytest.fixture
def api_rf() -> APIRequestFactory:
    """Provides an API request factory for manual request creation."""
    return APIRequestFactory()


@pytest.fixture()
def authenticated_client(users_list: Dict[str, object]) -> APIClient:
    """Provides an API client authenticated as first_simple_user."""
    client = APIClient()
    user = users_list["first_simple_user"]
    client.force_authenticate(user=user)
    return client


@pytest.fixture()
def admin_client(api_client: APIClient, users_list: Dict[str, object]) -> APIClient:
    """Provides an API client authenticated as an admin user."""
    user = users_list["admin_user"]
    user.is_staff = True
    user.save()
    api_client.force_authenticate(user=user)
    return api_client


# Recipe fixtures
@pytest.fixture
def recipe_owner(users_list: Dict[str, object]) -> object:
    """Returns the recipe owner user from users_list."""
    return users_list["recipe_owner_user"]


@pytest.fixture
def recipe_owner_client(recipe_owner: object) -> APIClient:
    """Provides an API client authenticated as the recipe owner."""
    client = APIClient()
    client.force_authenticate(user=recipe_owner)
    return client


@pytest.fixture
def recipe(recipe_owner: object) -> object:
    """Creates a single approved recipe owned by recipe_owner."""
    return RecipeFactory(
        user=recipe_owner, moderation_status=MODERATION_STATUS_APPROVED
    )


@pytest.fixture
def recipe_data(recipe_owner: object, category: object) -> Dict[str, object]:
    """Provides valid recipe creation data."""
    return {
        "category": category.id,
        "name": "test",
        "ingredients": "test - 1ks",
        "servings": 5,
    }


@pytest.fixture
def recipe_serializer_data(recipe_owner: object, category: object) -> Dict[str, object]:
    """Provides valid recipe serializer data."""
    return {
        "user": recipe_owner.id,
        "category": category.id,
        "name": "test",
        "slug": "123",
        "ingredients": "test - 1ks",
        "servings": 5,
        "announcement_text": "test",
        "recipe_text": "test",
        "moderation_status": MODERATION_STATUS_APPROVED,
        "created_at": "2026-01-02",
    }


@pytest.fixture()
def recipes() -> Dict[str, object]:
    """Creates a collection of recipes with different moderation statuses."""
    approved_recipes = RecipeFactory.create_batch(
        2, moderation_status=MODERATION_STATUS_APPROVED
    )
    in_process_recipes = RecipeFactory.create_batch(
        2, moderation_status=MODERATION_STATUS_IN_PROCESS
    )
    rejected_recipes = RecipeFactory.create_batch(
        2, moderation_status=MODERATION_STATUS_REJECTED
    )
    return {
        "approved_recipes": approved_recipes,
        "in_process_recipes": in_process_recipes,
        "all_recipes_len": len(approved_recipes)
        + len(in_process_recipes)
        + len(rejected_recipes),
    }


# Category fixtures
@pytest.fixture()
def category() -> object:
    """Creates a test category."""
    return CategoryFactory()


@pytest.fixture()
def category_data() -> Dict[str, str]:
    """Provides valid category creation data."""
    return {"name": "test"}


# Comment fixtures
@pytest.fixture
def comment_data(recipe) -> Dict[str, object]:
    """Provides valid comment creation data."""
    return {
        "recipe": recipe.id,
        "body": "This is a test comment",
    }


@pytest.fixture
def comment_serializer_data(recipe) -> Dict[str, object]:
    """Provides valid comment serializer data."""
    return {
        "recipe": recipe.id,
        "body": "This is a test comment",
    }


@pytest.fixture
def comment(users_list) -> object:
    """Creates a test comment owned by second_simple_user."""
    user = users_list["second_simple_user"]
    recipe = RecipeFactory(user=user, moderation_status=MODERATION_STATUS_APPROVED)
    return CommentFactory(user=user, recipe=recipe)


@pytest.fixture
def comment_owner_client(comment) -> APIClient:
    """Provides an API client authenticated as comment owner."""
    client = APIClient()
    client.force_authenticate(user=comment.user)
    return client


@pytest.fixture
def comments_fixture(authenticated_client, users_list) -> Dict[str, object]:
    """Creates multiple comments for testing."""
    user1 = users_list["first_simple_user"]
    user2 = users_list["second_simple_user"]

    recipe1 = RecipeFactory(user=user1, moderation_status=MODERATION_STATUS_APPROVED)
    recipe2 = RecipeFactory(user=user2, moderation_status=MODERATION_STATUS_APPROVED)

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


# Review fixtures
@pytest.fixture
def review_data(recipe) -> Dict[str, object]:
    """Provides valid review creation data."""
    return {
        "recipe": recipe.id,
        "rating": 5,
    }


@pytest.fixture
def review_serializer_data(recipe) -> Dict[str, object]:
    """Provides valid review serializer data."""
    return {
        "recipe": recipe.id,
        "rating": 5,
    }


@pytest.fixture
def review(users_list) -> object:
    """Creates a test review owned by second_simple_user."""
    user = users_list["second_simple_user"]
    recipe = RecipeFactory(moderation_status=MODERATION_STATUS_APPROVED)
    return ReviewFactory(user=user, recipe=recipe)


@pytest.fixture
def review_owner_client(review) -> APIClient:
    """Provides an API client authenticated as review owner."""
    client = APIClient()
    client.force_authenticate(user=review.user)
    return client


@pytest.fixture
def reviews_fixture(authenticated_client, users_list) -> Dict[str, object]:
    """Creates multiple reviews for testing."""
    user1 = users_list["first_simple_user"]
    user2 = users_list["second_simple_user"]

    recipe1 = RecipeFactory(user=user1, moderation_status=MODERATION_STATUS_APPROVED)
    recipe2 = RecipeFactory(user=user2, moderation_status=MODERATION_STATUS_APPROVED)

    reviews = [
        ReviewFactory(user=user1, recipe=recipe2),
        ReviewFactory(user=user2, recipe=recipe1),
        ReviewFactory(user=user1, recipe=recipe1),
    ]

    return {
        "all_reviews": reviews,
        "user1_reviews": [reviews[0], reviews[2]],
        "user2_reviews": [reviews[1]],
    }
