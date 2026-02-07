import pytest
from rest_framework import status

from recipehub.apps.recipes.api.serializers import CategorySerializer
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
    def test_serializer_fields(self, category, api_rf):
        request = api_rf.get("/")

        serializer = CategorySerializer(
            category,
            context={"request": request},
        )

        assert set(serializer.data.keys()) == {"url", "name", "slug"}

    def test_slug_is_read_only(self):
        serializer = CategorySerializer(
            data={"name": "Test Category", "slug": "custom-slug"}
        )

        assert serializer.is_valid()
        assert "slug" not in serializer.validated_data

    def test_name_field_present_in_validated_data(self):
        serializer = CategorySerializer(data={"name": "Test Category"})

        assert serializer.is_valid()
        assert serializer.validated_data["name"] == "Test Category"

    def test_slug_in_representation(self, category, api_rf):
        request = api_rf.get("/")

        serializer = CategorySerializer(
            category,
            context={"request": request},
        )

        assert serializer.data["slug"] == category.slug

    def test_url_field(self, category, api_rf):
        request = api_rf.get("/")

        serializer = CategorySerializer(
            category,
            context={"request": request},
        )

        assert "url" in serializer.data
        assert str(category.id) in serializer.data["url"]
