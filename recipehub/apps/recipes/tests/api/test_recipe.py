import pytest
from rest_framework import status

from recipehub.apps.recipes.models import Recipe
from recipehub.factories import RecipeFactory

ENDPOINT = "/api/recipes/"


@pytest.mark.django_db
class TestPaginationRecipeList:
    PAGE_SIZE = 10

    def test_list_recipes(self, authenticated_client):
        RecipeFactory.create_batch(15, moderation_status="approved")
        response = authenticated_client.get(ENDPOINT)

        assert response.status_code == status.HTTP_200_OK
        assert all(key in response.data for key in ['count', 'previous', 'next', 'results'])
        assert len(response.data["results"]) <= self.PAGE_SIZE


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
        response = client.patch(
            f"{ENDPOINT}{recipe.slug}/", recipe_data, format="json"
        )
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
    def test_delete_permissions(
            self, client_fixture, expected_status, recipe, request
    ):
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
