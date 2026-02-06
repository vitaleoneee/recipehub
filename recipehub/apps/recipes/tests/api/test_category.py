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

    def test_list_categories_empty(self, api_client):
        """Test listing when no categories exist"""
        response = api_client.get(ENDPOINT)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 0


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
            ("admin_client", status.HTTP_204_NO_CONTENT),
        ],
    )
    def test_delete_permissions(self, client_fixture, expected_status, request):
        category = CategoryFactory()
        client = request.getfixturevalue(client_fixture)
        response = client.delete(f"{ENDPOINT}{category.id}/")
        assert response.status_code == expected_status

    @pytest.mark.parametrize(
        "client_fixture,expected_status",
        [
            ("api_client", status.HTTP_401_UNAUTHORIZED),
            ("authenticated_client", status.HTTP_403_FORBIDDEN),
            ("admin_client", status.HTTP_200_OK),
        ],
    )
    def test_update_permissions(
        self, client_fixture, expected_status, category_data, request
    ):
        category = CategoryFactory()
        client = request.getfixturevalue(client_fixture)
        response = client.put(f"{ENDPOINT}{category.id}/", category_data, format="json")
        assert response.status_code == expected_status

    @pytest.mark.parametrize(
        "client_fixture,expected_status",
        [
            ("api_client", status.HTTP_401_UNAUTHORIZED),
            ("authenticated_client", status.HTTP_403_FORBIDDEN),
            ("admin_client", status.HTTP_200_OK),
        ],
    )
    def test_patch_permissions(
        self, client_fixture, expected_status, category_data, request
    ):
        category = CategoryFactory()
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
            ("admin_client", status.HTTP_201_CREATED),
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

    def test_create_category(self, admin_client, category_data):
        response = admin_client.post(ENDPOINT, category_data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == category_data["name"]
        assert Category.objects.filter(name=category_data["name"]).exists()

    def test_create_category_invalid_data(self, admin_client):
        response = admin_client.post(ENDPOINT, {"name": ""}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_category_duplicate_name(self, admin_client, category):
        """Test that duplicate category names are handled"""
        response = admin_client.post(ENDPOINT, {"name": category.name}, format="json")
        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_201_CREATED,
        ]

    def test_update_category(self, admin_client, category_data):
        category = CategoryFactory()
        original_slug = category.slug
        response = admin_client.put(
            f"{ENDPOINT}{category.id}/", category_data, format="json"
        )

        assert response.status_code == status.HTTP_200_OK
        category.refresh_from_db()
        assert category.name == category_data["name"]
        assert category.slug == original_slug

    def test_patch_category(self, admin_client):
        category = CategoryFactory()
        new_name = "Updated Category Name"
        response = admin_client.patch(
            f"{ENDPOINT}{category.id}/", {"name": new_name}, format="json"
        )

        assert response.status_code == status.HTTP_200_OK
        category.refresh_from_db()
        assert category.name == new_name

    def test_destroy_category(self, admin_client):
        category = CategoryFactory()
        category_id = category.id
        response = admin_client.delete(f"{ENDPOINT}{category_id}/")

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Category.objects.filter(id=category_id).exists()


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

    def test_slug_auto_generation(self, admin_client):
        """Test that slug is auto-generated from name"""
        response = admin_client.post(
            ENDPOINT, {"name": "My Test Category"}, format="json"
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["slug"] == "my-test-category"

    def test_url_field_present(self, api_client, category):
        """Test that URL field is present in response"""
        response = api_client.get(f"{ENDPOINT}{category.id}/")

        assert response.status_code == status.HTTP_200_OK
        assert "url" in response.data
        assert f"/api/categories/{category.id}/" in response.data["url"]
