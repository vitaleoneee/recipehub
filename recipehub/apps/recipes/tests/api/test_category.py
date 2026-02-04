import pytest
from rest_framework import status

from recipehub.apps.recipes.models import Category
from recipehub.factories import CategoryFactory

ENDPOINT = "/api/categories/"


@pytest.mark.django_db
class TestCategoryList:
    def test_list_categories(self, api_client):
        categories = CategoryFactory.create_batch(5)
        response = api_client.get(ENDPOINT)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == len(categories)


@pytest.mark.django_db
class TestCategoryRetrieve:
    def test_retrieve_category(self, api_client, category):
        response = api_client.get(f"{ENDPOINT}{category.id}/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == category.name

    def test_retrieve_not_found(self, api_client):
        response = api_client.get(f"{ENDPOINT}999999/")
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestCategoryPermissions:
    """Permissions rights check tests for private operations"""

    @pytest.mark.parametrize(
        "client_fixture,expected_status",
        [
            ("api_client", status.HTTP_401_UNAUTHORIZED),
            ("authenticated_client", status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_delete_permissions(
        self, client_fixture, expected_status, category, request
    ):
        client = request.getfixturevalue(client_fixture)
        response = client.delete(f"{ENDPOINT}{category.id}/")
        assert response.status_code == expected_status

    @pytest.mark.parametrize(
        "client_fixture,expected_status",
        [
            ("api_client", status.HTTP_401_UNAUTHORIZED),
            ("authenticated_client", status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_update_permissions(
        self, client_fixture, expected_status, category, category_data, request
    ):
        client = request.getfixturevalue(client_fixture)
        response = client.put(f"{ENDPOINT}{category.id}/", category_data, format="json")
        assert response.status_code == expected_status

    @pytest.mark.parametrize(
        "client_fixture,expected_status",
        [
            ("api_client", status.HTTP_401_UNAUTHORIZED),
            ("authenticated_client", status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_patch_permissions(
        self, client_fixture, expected_status, category, category_data, request
    ):
        client = request.getfixturevalue(client_fixture)
        response = client.patch(
            f"{ENDPOINT}{category.id}/", category_data, format="json"
        )
        assert response.status_code == expected_status

    @pytest.mark.parametrize(
        "client_fixture,expected_status",
        [
            ("api_client", status.HTTP_401_UNAUTHORIZED),
            ("authenticated_client", status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_create_permissions(
        self, client_fixture, expected_status, category_data, request
    ):
        client = request.getfixturevalue(client_fixture)
        response = client.post(ENDPOINT, category_data, format="json")
        assert response.status_code == expected_status


@pytest.mark.django_db
class TestCategoryAdminOperations:
    """Operation tests for admin"""

    def test_destroy_category(self, category, admin_client):
        response = admin_client.delete(f"{ENDPOINT}{category.id}/")

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Category.objects.filter(id=category.id).exists()

    def test_update_category(self, category, admin_client, category_data):
        response = admin_client.put(
            f"{ENDPOINT}{category.id}/", category_data, format="json"
        )

        assert response.status_code == status.HTTP_200_OK
        updated_category = Category.objects.get(id=category.id)
        assert updated_category.name == "test"

    def test_patch_category(self, category, admin_client, category_data):
        response = admin_client.patch(
            f"{ENDPOINT}{category.id}/", category_data, format="json"
        )

        assert response.status_code == status.HTTP_200_OK
        updated_category = Category.objects.get(id=category.id)
        assert updated_category.name == "test"

    def test_create_category(self, admin_client, category_data):
        response = admin_client.post(ENDPOINT, category_data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "test"
        assert Category.objects.filter(name="test").exists()

    def test_create_category_invalid_data(self, admin_client):
        response = admin_client.post(ENDPOINT, {"name": ""}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestCategorySerializer:
    def test_serializer_fields(self, admin_client, category_data):
        """Checks that the serializer returns the correct fields"""
        response = admin_client.post(ENDPOINT, category_data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert set(response.data.keys()) == {"url", "name", "slug"}
        assert "url" in response.data
        assert "name" in response.data
        assert "slug" in response.data

    def test_slug_is_read_only(self, admin_client):
        """Checks that the slug cannot be passed when creating"""
        response = admin_client.post(
            ENDPOINT, {"name": "Test Category", "slug": "custom-slug"}, format="json"
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["slug"] != "custom-slug"
        assert response.data["slug"] == "test-category"
