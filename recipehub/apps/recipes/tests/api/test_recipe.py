import pytest
from rest_framework import status

from recipehub.apps.recipes.api.serializers import (
    RecipeModerationSerializer,
    RecipeSerializer,
)
from recipehub.apps.recipes.models import Recipe
from recipehub.apps.users.models import UserRecipeFavorite
from recipehub.factories import RecipeFactory, CategoryFactory

ENDPOINT = "/api/recipes/"


@pytest.mark.django_db
class TestPaginationRecipeList:
    PAGE_SIZE = 10

    def test_list_recipes(self, authenticated_client):
        RecipeFactory.create_batch(15, moderation_status="approved")
        response = authenticated_client.get(ENDPOINT)

        assert response.status_code == status.HTTP_200_OK
        assert all(
            key in response.data for key in ["count", "previous", "next", "results"]
        )
        assert len(response.data["results"]) <= self.PAGE_SIZE


@pytest.mark.django_db
class TestSearchRecipeList:
    def test_search_recipes(self, authenticated_client):
        RecipeFactory(name="Tomato Soup", moderation_status="approved")
        RecipeFactory(name="Chicken Soup", moderation_status="approved")
        response = authenticated_client.get(f"{ENDPOINT}?search=tomato")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["name"] == "Tomato Soup"


@pytest.mark.django_db
class TestOrderingRecipeList:
    def test_ordering_recipe(self, authenticated_client):
        r1 = RecipeFactory(
            name="A Recipe", cooking_time=10, moderation_status="approved"
        )
        r2 = RecipeFactory(
            name="B Recipe", cooking_time=5, moderation_status="approved"
        )

        response = authenticated_client.get(f"{ENDPOINT}?ordering=-cooking_time")
        assert response.status_code == status.HTTP_200_OK
        results = response.data["results"]
        assert results[0]["name"] == r1.name
        assert results[1]["name"] == r2.name


@pytest.mark.django_db
class TestFilteringRecipeList:
    def test_filter_category_and_cooking_time(self, authenticated_client):
        category = CategoryFactory(name="Dessert")
        r1 = RecipeFactory(
            category=category, cooking_time=10, moderation_status="approved"
        )
        r2 = RecipeFactory(cooking_time=15, moderation_status="approved")

        response = authenticated_client.get(f"{ENDPOINT}?category__name=Dessert")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["name"] == r1.name

        response = authenticated_client.get(f"{ENDPOINT}?cooking_time__gte=12")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["name"] == r2.name


@pytest.mark.django_db
class TestRecipePermissions:
    """Permissions rights check tests for private operations"""

    @pytest.mark.parametrize(
        "client_fixture,expected_status",
        [
            ("api_client", status.HTTP_401_UNAUTHORIZED),
            ("authenticated_client", status.HTTP_200_OK),
        ],
    )
    def test_retrieve_permissions(
        self, client_fixture, expected_status, recipe, request
    ):
        client = request.getfixturevalue(client_fixture)
        response = client.get(f"{ENDPOINT}{recipe.slug}/")
        assert response.status_code == expected_status

    @pytest.mark.parametrize(
        "client_fixture,expected_status",
        [
            ("api_client", status.HTTP_401_UNAUTHORIZED),
            ("authenticated_client", status.HTTP_201_CREATED),
        ],
    )
    def test_create_permissions(
        self, client_fixture, expected_status, recipe_data, request
    ):
        client = request.getfixturevalue(client_fixture)
        response = client.post(ENDPOINT, data=recipe_data, format="json")
        assert response.status_code == expected_status

    @pytest.mark.parametrize(
        "client_fixture,expected_status",
        [
            ("api_client", status.HTTP_401_UNAUTHORIZED),
            ("authenticated_client", status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_update_permissions(
        self, client_fixture, expected_status, recipe, recipe_data, request
    ):
        client = request.getfixturevalue(client_fixture)
        response = client.put(f"{ENDPOINT}{recipe.slug}/", recipe_data, format="json")
        assert response.status_code == expected_status

    @pytest.mark.parametrize(
        "client_fixture,expected_status",
        [
            ("api_client", status.HTTP_401_UNAUTHORIZED),
            ("authenticated_client", status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_patch_permissions(
        self, client_fixture, expected_status, recipe, recipe_data, request
    ):
        client = request.getfixturevalue(client_fixture)
        response = client.patch(f"{ENDPOINT}{recipe.slug}/", recipe_data, format="json")
        assert response.status_code == expected_status

    @pytest.mark.parametrize(
        "client_fixture,expected_status",
        [
            ("api_client", status.HTTP_401_UNAUTHORIZED),
            ("authenticated_client", status.HTTP_403_FORBIDDEN),
            ("recipe_owner_client", status.HTTP_204_NO_CONTENT),
            ("admin_client", status.HTTP_204_NO_CONTENT),
        ],
    )
    def test_delete_permissions(self, client_fixture, expected_status, recipe, request):
        client = request.getfixturevalue(client_fixture)
        response = client.delete(f"{ENDPOINT}{recipe.slug}/")
        assert response.status_code == expected_status


@pytest.mark.django_db
class TestDefaultUserRecipeOperations:
    def test_list_recipes(self, api_client, recipes):
        response = api_client.get(ENDPOINT)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == len(recipes["approved_recipes"])

    def test_list_not_approved_recipes(self, api_client, recipes):
        response = api_client.get(ENDPOINT)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == len(recipes["approved_recipes"])

    def test_retrieve_recipe(self, recipe, authenticated_client):
        response = authenticated_client.get(f"{ENDPOINT}{recipe.slug}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["slug"] == recipe.slug

    def test_retrieve_not_approved_recipe(self, authenticated_client):
        recipe = RecipeFactory(moderation_status="in_process")
        response = authenticated_client.get(f"{ENDPOINT}{recipe.slug}/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_recipe(self, authenticated_client, recipe_data):
        response = authenticated_client.post(ENDPOINT, recipe_data, format="json")
        name = recipe_data["name"]

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == name
        assert Recipe.objects.filter(name=name).exists()

    def test_create_recipe_invalid_data(self, authenticated_client):
        response = authenticated_client.post(ENDPOINT, {"name": ""}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_owned_recipe(self, recipe_owner_client, recipe, recipe_data):
        recipe_data["name"] = "Updated Recipe Name"
        response = recipe_owner_client.put(
            f"{ENDPOINT}{recipe.slug}/", recipe_data, format="json"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == recipe_data["name"]

        recipe.refresh_from_db()
        assert recipe.name == recipe_data["name"]

    def test_update_not_owned_recipe(self, recipe, authenticated_client, recipe_data):
        original_name = recipe.name
        recipe_data["name"] = "Updated Recipe Name"
        response = authenticated_client.put(
            f"{ENDPOINT}{recipe.slug}/", recipe_data, format="json"
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

        recipe.refresh_from_db()
        assert recipe.name == original_name

    def test_partial_update_owned_recipe(self, recipe_owner_client, recipe):
        new_name = "Partially Updated Recipe"
        response = recipe_owner_client.patch(
            f"{ENDPOINT}{recipe.slug}/", {"name": new_name}, format="json"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == new_name

        recipe.refresh_from_db()
        assert recipe.name == new_name

    def test_partial_update_not_owned_recipe(self, authenticated_client, recipe):
        original_name = recipe.name
        response = authenticated_client.patch(
            f"{ENDPOINT}{recipe.slug}/", {"name": "New Name"}, format="json"
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

        recipe.refresh_from_db()
        assert recipe.name == original_name

    def test_delete_owned_recipe(self, recipe_owner_client, recipe):
        recipe_id = recipe.id
        response = recipe_owner_client.delete(f"{ENDPOINT}{recipe.slug}/")

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Recipe.objects.filter(id=recipe_id).exists()

    def test_delete_not_owned_recipe(self, authenticated_client, recipe):
        recipe_id = recipe.id
        response = authenticated_client.delete(f"{ENDPOINT}{recipe.slug}/")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Recipe.objects.filter(id=recipe_id).exists()


@pytest.mark.django_db
class TestAdminUserRecipeOperations:
    def test_admin_list_all_recipes(self, admin_client, recipes):
        response = admin_client.get(ENDPOINT)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == recipes["all_recipes_len"]

    def test_admin_retrieve_not_approved_recipe(self, admin_client):
        recipe = RecipeFactory(moderation_status="in_process")
        response = admin_client.get(f"{ENDPOINT}{recipe.slug}/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["slug"] == recipe.slug

    def test_admin_update_any_recipe(self, admin_client, recipe, recipe_data):
        recipe_data["name"] = "Admin Updated Recipe"
        response = admin_client.put(
            f"{ENDPOINT}{recipe.slug}/", recipe_data, format="json"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == recipe_data["name"]

        recipe.refresh_from_db()
        assert recipe.name == recipe_data["name"]

    def test_admin_partial_update_any_recipe(self, admin_client, recipe):
        new_name = "Admin Partial Update"
        response = admin_client.patch(
            f"{ENDPOINT}{recipe.slug}/", {"name": new_name}, format="json"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == new_name

        recipe.refresh_from_db()
        assert recipe.name == new_name

    def test_admin_delete_any_recipe(self, admin_client, recipe):
        recipe_id = recipe.id
        response = admin_client.delete(f"{ENDPOINT}{recipe.slug}/")

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Recipe.objects.filter(id=recipe_id).exists()

    def test_admin_create_recipe(self, admin_client, recipe_data):
        response = admin_client.post(ENDPOINT, recipe_data, format="json")
        name = recipe_data["name"]

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == name
        assert Recipe.objects.filter(name=name).exists()


@pytest.mark.django_db
class TestRecipeCustomActions:
    """Tests for custom actions in RecipeViewSet"""

    # My Recipes action tests
    def test_my_recipes_permissions(self, api_client):
        """Unauthorized users cannot access my-recipes"""
        response = api_client.get(f"{ENDPOINT}my-recipes/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_my_recipes_authenticated(self, authenticated_client, users_list):
        """User can see only their own recipes"""
        user = users_list["first_simple_user"]

        # Create recipes for current user
        RecipeFactory.create_batch(3, user=user, moderation_status="approved")

        # Create recipes for other users
        RecipeFactory.create_batch(2, moderation_status="approved")

        response = authenticated_client.get(f"{ENDPOINT}my-recipes/")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3
        assert Recipe.objects.filter(user=user).count() == 3

    def test_my_recipes_empty(self, authenticated_client):
        """User with no recipes gets empty list"""
        response = authenticated_client.get(f"{ENDPOINT}my-recipes/")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

    # Best Recipes action tests
    def test_best_recipes_permissions(self, api_client):
        """Unauthorized users cannot access best-recipes"""
        response = api_client.get(f"{ENDPOINT}best-recipes/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_best_recipes_authenticated(self, authenticated_client):
        """Authenticated user can access best recipes"""
        RecipeFactory.create_batch(5, moderation_status="approved")

        response = authenticated_client.get(f"{ENDPOINT}best-recipes/")

        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)

    # Moderation: in-process recipes
    def test_in_process_recipes_permissions(self, authenticated_client):
        """Regular users cannot access in-process recipes"""
        response = authenticated_client.get(f"{ENDPOINT}in-process/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_in_process_recipes_admin(self, admin_client):
        """Admin can see recipes in moderation"""
        RecipeFactory.create_batch(2, moderation_status="in_process")
        RecipeFactory.create_batch(3, moderation_status="approved")

        response = admin_client.get(f"{ENDPOINT}in-process/")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
        assert all(
            recipe["moderation_status"] == "in_process" for recipe in response.data
        )

    # Moderation: moderate action
    def test_moderate_recipe_permissions(self, authenticated_client, recipe):
        """Regular users cannot moderate recipes"""
        response = authenticated_client.patch(
            f"{ENDPOINT}{recipe.slug}/moderate/", {"status": "approved"}, format="json"
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_moderate_recipe_admin(self, admin_client):
        """Admin can moderate recipes"""
        recipe = RecipeFactory(moderation_status="in_process")

        response = admin_client.patch(
            f"{ENDPOINT}{recipe.slug}/moderate/", {"status": "approved"}, format="json"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "approved"
        assert response.data["slug"] == recipe.slug

        recipe.refresh_from_db()
        assert recipe.moderation_status == "approved"

    def test_moderate_recipe_invalid_status(self, admin_client, recipe):
        """Invalid moderation status returns validation error"""
        response = admin_client.patch(
            f"{ENDPOINT}{recipe.slug}/moderate/",
            {"status": "invalid_status"},
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    # Favorites: add to favorites
    def test_add_to_favorites_permissions(self, api_client, recipe):
        """Unauthorized users cannot add to favorites"""
        response = api_client.post(f"{ENDPOINT}{recipe.slug}/favorite/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_add_to_favorites(self, authenticated_client, recipe):
        """User can add recipe to favorites"""
        response = authenticated_client.post(f"{ENDPOINT}{recipe.slug}/favorite/")

        assert response.status_code == status.HTTP_201_CREATED
        assert UserRecipeFavorite.objects.filter(
            user=authenticated_client.handler._force_user, recipe=recipe
        ).exists()

    def test_add_own_recipe_to_favorites(self, recipe_owner_client, recipe):
        """User cannot add their own recipe to favorites"""
        response = recipe_owner_client.post(f"{ENDPOINT}{recipe.slug}/favorite/")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "cannot add your recipe to favorites" in response.data["detail"].lower()

    def test_add_already_favorited_recipe(
        self, authenticated_client, recipe, users_list
    ):
        """Cannot add same recipe to favorites twice"""
        user = users_list["first_simple_user"]
        UserRecipeFavorite.objects.create(user=user, recipe=recipe)

        response = authenticated_client.post(f"{ENDPOINT}{recipe.slug}/favorite/")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already in favorites" in response.data["detail"].lower()

    # Favorites: remove from favorites
    def test_remove_from_favorites(self, authenticated_client, recipe, users_list):
        """User can remove recipe from favorites"""
        user = users_list["first_simple_user"]
        UserRecipeFavorite.objects.create(user=user, recipe=recipe)

        response = authenticated_client.delete(f"{ENDPOINT}{recipe.slug}/favorite/")

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not UserRecipeFavorite.objects.filter(user=user, recipe=recipe).exists()

    def test_remove_not_favorited_recipe(self, authenticated_client, recipe):
        """Cannot remove recipe that's not in favorites"""
        response = authenticated_client.delete(f"{ENDPOINT}{recipe.slug}/favorite/")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "not in favorites" in response.data["detail"].lower()

    def test_remove_favorite_not_owned_recipe(
        self, authenticated_client, recipe, users_list
    ):
        """Cannot remove favorite that belongs to another user"""
        other_user = users_list["second_simple_user"]
        UserRecipeFavorite.objects.create(user=other_user, recipe=recipe)
        response = authenticated_client.delete(f"{ENDPOINT}{recipe.slug}/favorite/")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "not in favorites" in response.data["detail"].lower()

    # Recipe Builder action tests
    def test_recipe_builder_permissions(self, api_client):
        """Unauthorized users cannot access recipe builder"""
        response = api_client.get(f"{ENDPOINT}builder/?ingredients=tomato,cheese")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_recipe_builder_with_ingredients(self, authenticated_client):
        """Recipe builder returns recipes with specified ingredients"""
        RecipeFactory(ingredients="tomato, cheese, basil", moderation_status="approved")
        RecipeFactory(ingredients="chicken, garlic", moderation_status="approved")
        RecipeFactory(ingredients="tomato, onion", moderation_status="approved")

        response = authenticated_client.get(
            f"{ENDPOINT}builder/?ingredients=tomato,cheese"
        )

        assert response.status_code == status.HTTP_200_OK
        assert "recipes" in response.data
        assert len(response.data["recipes"]) == 2

    def test_recipe_builder_no_ingredients(self, authenticated_client):
        """Recipe builder with no ingredients returns empty or all recipes"""
        RecipeFactory.create_batch(3, moderation_status="approved")

        response = authenticated_client.get(f"{ENDPOINT}builder/")

        assert response.status_code == status.HTTP_200_OK
        assert "recipes" in response.data
        assert len(response.data["recipes"]) == 3

    def test_recipe_builder_no_matches(self, authenticated_client):
        """Recipe builder returns empty when no recipes match"""
        RecipeFactory(ingredients="tomato, cheese", moderation_status="approved")

        response = authenticated_client.get(
            f"{ENDPOINT}builder/?ingredients=banana,strawberry"
        )

        assert response.status_code == status.HTTP_200_OK
        assert "recipes" in response.data
        assert len(response.data["recipes"]) == 0

    def test_recipe_builder_only_approved_recipes(self, authenticated_client):
        """Recipe builder returns only approved recipes"""
        RecipeFactory(ingredients="tomato", moderation_status="approved")
        RecipeFactory(ingredients="tomato", moderation_status="in_process")
        RecipeFactory(ingredients="tomato", moderation_status="rejected")

        response = authenticated_client.get(f"{ENDPOINT}builder/?ingredients=tomato")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["recipes"]) == 1
        assert response.data["recipes"][0]["moderation_status"] == "approved"


@pytest.mark.django_db
class TestRecipeModerationSerializer:
    def test_serializer_valid_status_field(self, admin_client):
        serializer = RecipeModerationSerializer(data={"status": "approved"})
        assert serializer.is_valid()
        assert serializer.validated_data["status"] == "approved"

    def test_serializer_invalid_status_field(self, admin_client):
        serializer = RecipeModerationSerializer(data={"status": "wrong"})
        assert not serializer.is_valid()
        assert "status" in serializer.errors


@pytest.mark.django_db
class TestRecipeSerializer:
    @pytest.mark.parametrize(
        "field,value",
        [
            ("user", 1),
            ("created_at", "2026-01-01"),
            ("slug", "test-slug"),
            ("moderation_status", "approved"),
        ],
    )
    def test_read_only_fields(self, field, value, recipe_serializer_data):
        recipe_serializer_data[field] = value

        serializer = RecipeSerializer(data=recipe_serializer_data)

        assert serializer.is_valid(), serializer.errors
        assert field not in serializer.validated_data

    def test_create_sets_user(
        self, recipe_serializer_data, authenticated_client, api_rf
    ):
        request = api_rf.post("/recipes/")
        request.user = authenticated_client.handler._force_user

        serializer = RecipeSerializer(
            data=recipe_serializer_data, context={"request": request}
        )

        assert serializer.is_valid(), serializer.errors

        recipe = serializer.save()

        assert recipe.user == authenticated_client.handler._force_user

    def test_user_is_string_related(self, recipe):
        serializer = RecipeSerializer(recipe)

        assert serializer.data["user"] == str(recipe.user)

    def test_ingredients_normalized(self, recipe_serializer_data):
        recipe_serializer_data["ingredients"] = "Tomato - 2 pcs\nSalt - 1 tsp"

        serializer = RecipeSerializer(data=recipe_serializer_data)

        assert serializer.is_valid(), serializer.errors

        assert serializer.validated_data["ingredients"] == (
            "tomato - 2 pcs\nsalt - 1 tsp"
        )

    def test_ingredients_invalid_format(self, recipe_serializer_data):
        recipe_serializer_data["ingredients"] = "Tomato 2 pcs"

        serializer = RecipeSerializer(data=recipe_serializer_data)

        assert not serializer.is_valid()
        assert "ingredients" in serializer.errors
