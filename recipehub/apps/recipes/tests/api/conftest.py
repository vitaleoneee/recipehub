import pytest

from rest_framework.test import APIClient, APIRequestFactory

from recipehub.factories import CategoryFactory, RecipeFactory


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
def category():
    return CategoryFactory()


@pytest.fixture()
def category_data():
    return {"name": "test"}


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
