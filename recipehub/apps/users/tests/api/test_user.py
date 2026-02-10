import pytest
from rest_framework import status
from django.contrib.auth import get_user_model

from recipehub.apps.users.api.serializers import UserSerializer, RegisterSerializer
from recipehub.factories import UserFactory

User = get_user_model()

ENDPOINT = "/api/users/"
REGISTER_ENDPOINT = "/api/auth/register/"


@pytest.mark.django_db
class TestUserPermissions:
    """Permissions rights check tests for user operations"""

    @pytest.mark.parametrize(
        "client_fixture,expected_status",
        [
            ("api_client", status.HTTP_401_UNAUTHORIZED),
            ("authenticated_client", status.HTTP_403_FORBIDDEN),
            ("admin_client", status.HTTP_200_OK),
        ],
    )
    def test_list_permissions(self, client_fixture, expected_status, request):
        """Only admins can list all users"""
        client = request.getfixturevalue(client_fixture)
        response = client.get(ENDPOINT)
        assert response.status_code == expected_status

    @pytest.mark.parametrize(
        "client_fixture,expected_status",
        [
            ("api_client", status.HTTP_401_UNAUTHORIZED),
            ("authenticated_client", status.HTTP_403_FORBIDDEN),
            ("admin_client", status.HTTP_200_OK),
        ],
    )
    def test_retrieve_user_permissions(
            self, client_fixture, expected_status, request, users_list
    ):
        """Only admins can retrieve specific user details"""
        client = request.getfixturevalue(client_fixture)
        user = users_list["recipe_owner_user"]
        response = client.get(f"{ENDPOINT}{user.id}/")
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
            self, client_fixture, expected_status, request, users_list, sample_image
    ):
        """Only admins can update users"""
        client = request.getfixturevalue(client_fixture)
        user = users_list["recipe_owner_user"]
        user_data = {
            "username": "updated_user",
            "email": "updated@example.com",
            "date_of_birth": "2000-01-01",
        }
        response = client.put(f"{ENDPOINT}{user.id}/", user_data, format="json")
        assert response.status_code == expected_status

    @pytest.mark.parametrize(
        "client_fixture,expected_status",
        [
            ("api_client", status.HTTP_401_UNAUTHORIZED),
            ("authenticated_client", status.HTTP_403_FORBIDDEN),
            ("admin_client", status.HTTP_204_NO_CONTENT),
        ],
    )
    def test_delete_permissions(
            self, client_fixture, expected_status, request, users_list
    ):
        """Only admins can delete users"""
        client = request.getfixturevalue(client_fixture)
        user = users_list["recipe_owner_user"]
        response = client.delete(f"{ENDPOINT}{user.id}/")
        assert response.status_code == expected_status


@pytest.mark.django_db
class TestAdminUserOperations:
    """Tests for admin user operations"""

    def test_admin_list_users(self, admin_client):
        """Admin can list all users"""
        response = admin_client.get(ENDPOINT)

        assert response.status_code == status.HTTP_200_OK
        assert "results" in response.data

    def test_admin_retrieve_user(self, admin_client, users_list):
        """Admin can retrieve specific user"""
        user = users_list["recipe_owner_user"]
        response = admin_client.get(f"{ENDPOINT}{user.id}/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == user.id
        assert response.data["username"] == user.username

    def test_admin_update_user(self, admin_client, users_list):
        """Admin can update user"""
        user = users_list["recipe_owner_user"]
        user_data = {
            "username": "updated_username",
            "email": "updated@example.com",
            "date_of_birth": "2000-01-01",
        }
        response = admin_client.put(f"{ENDPOINT}{user.id}/", user_data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["username"] == user_data["username"]

        user.refresh_from_db()
        assert user.username == user_data["username"]

    def test_admin_partial_update_user(self, admin_client, users_list):
        """Admin can partially update user"""
        user = users_list["recipe_owner_user"]
        new_email = "newemail@example.com"
        response = admin_client.patch(
            f"{ENDPOINT}{user.id}/", {"email": new_email}, format="json"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == new_email

        user.refresh_from_db()
        assert user.email == new_email

    def test_admin_delete_user(self, admin_client, users_list):
        """Admin can delete user"""
        user = users_list["recipe_owner_user"]
        user_id = user.id
        response = admin_client.delete(f"{ENDPOINT}{user.id}/")

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not User.objects.filter(id=user_id).exists()


@pytest.mark.django_db
class TestMeEndpoint:
    """Tests for the /me endpoint"""

    def test_me_unauthorized(self, api_client):
        """Unauthorized users cannot access /me"""
        response = api_client.get(f"{ENDPOINT}me/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_me_get_authenticated(self, authenticated_client, users_list):
        """Authenticated user can get their own profile"""
        user = users_list["first_simple_user"]
        response = authenticated_client.get(f"{ENDPOINT}me/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == user.id
        assert response.data["username"] == user.username
        assert response.data["email"] == user.email

    def test_me_put_authenticated(self, authenticated_client, users_list):
        """Authenticated user can update their profile with PUT"""
        user = users_list["first_simple_user"]
        new_data = {
            "username": "updated_me",
            "email": "me_updated@example.com",
            "date_of_birth": "1990-05-15",
        }
        response = authenticated_client.put(f"{ENDPOINT}me/", new_data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["username"] == new_data["username"]
        assert response.data["email"] == new_data["email"]

        user.refresh_from_db()
        assert user.username == new_data["username"]

    def test_me_patch_authenticated(self, authenticated_client, users_list):
        """Authenticated user can partially update their profile with PATCH"""
        user = users_list["first_simple_user"]
        new_email = "patched@example.com"
        response = authenticated_client.patch(
            f"{ENDPOINT}me/", {"email": new_email}, format="json"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == new_email

        user.refresh_from_db()
        assert user.email == new_email

    def test_me_cannot_modify_read_only_fields(self, authenticated_client, users_list):
        """User cannot modify read-only fields in /me"""
        user = users_list["first_simple_user"]
        response = authenticated_client.patch(
            f"{ENDPOINT}me/",
            {"id": 99999},
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.id != 99999


@pytest.mark.django_db
class TestUserRecipesEndpoint:
    """Tests for the /users/{id}/recipes endpoint"""

    def test_recipes_unauthorized(self, api_client, users_list):
        """Unauthorized users cannot access user's recipes"""
        user = users_list["recipe_owner_user"]
        response = api_client.get(f"{ENDPOINT}{user.id}/recipes/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_recipes_authenticated_can_access(
            self, authenticated_client, users_list, recipe
    ):
        """Authenticated user can get specific user's recipes"""
        user = users_list["recipe_owner_user"]
        response = authenticated_client.get(f"{ENDPOINT}{user.id}/recipes/")

        assert response.status_code == status.HTTP_200_OK
        assert "results" in response.data

    def test_recipes_nonexistent_user(self, authenticated_client):
        """Getting recipes for nonexistent user returns 404"""
        response = authenticated_client.get(f"{ENDPOINT}99999/recipes/")
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestUserRegistration:
    """Tests for user registration"""

    def test_register_valid_data(self, api_client):
        """User can register with valid data"""
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "SecurePass123!",
            "date_of_birth": "2000-01-01",
        }
        response = api_client.post(REGISTER_ENDPOINT, user_data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert "access" in response.data
        assert "refresh" in response.data
        assert User.objects.filter(username=user_data["username"]).exists()

    def test_register_missing_required_field(self, api_client):
        """Registration fails with missing required field"""
        user_data = {
            "email": "newuser@example.com",
            "password": "SecurePass123!",
        }
        response = api_client.post(REGISTER_ENDPOINT, user_data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "username" in response.data

    def test_register_duplicate_username(self, api_client):
        """Registration fails with duplicate username"""
        UserFactory(username="existinguser")
        user_data = {
            "username": "existinguser",
            "email": "different@example.com",
            "password": "SecurePass123!",
        }
        response = api_client.post(REGISTER_ENDPOINT, user_data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_invalid_email(self, api_client):
        """Registration fails with invalid email"""
        user_data = {
            "username": "newuser",
            "email": "invalid-email",
            "password": "SecurePass123!",
        }
        response = api_client.post(REGISTER_ENDPOINT, user_data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_returns_tokens(self, api_client):
        """Registration returns valid JWT tokens"""
        user_data = {
            "username": "tokenuser",
            "email": "token@example.com",
            "password": "SecurePass123!",
        }
        response = api_client.post(REGISTER_ENDPOINT, user_data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert "access" in response.data
        assert "refresh" in response.data
        # Verify tokens are not empty strings
        assert response.data["access"]
        assert response.data["refresh"]


@pytest.mark.django_db
class TestUserSerializer:
    """Tests for UserSerializer behavior"""

    def test_serializer_fields(self, users_list):
        """UserSerializer includes correct fields"""
        user = users_list["recipe_owner_user"]
        serializer = UserSerializer(user)

        assert "id" in serializer.data
        assert "username" in serializer.data
        assert "email" in serializer.data
        assert "date_of_birth" in serializer.data
        assert "photo" in serializer.data

    def test_serializer_read_only_id(self, users_list):
        """ID field is read-only"""
        user = users_list["recipe_owner_user"]
        data = {
            "id": 99999,
            "username": "updated",
            "email": "updated@example.com",
        }

        serializer = UserSerializer(user, data=data, partial=True)
        assert serializer.is_valid()
        serializer.save()

        user.refresh_from_db()
        assert user.id != 99999

    def test_serializer_update_user(self, users_list):
        """Serializer can update user data"""
        user = users_list["recipe_owner_user"]
        new_data = {
            "username": "newusername",
            "email": "new@example.com",
            "date_of_birth": "1995-06-20",
        }

        serializer = UserSerializer(user, data=new_data, partial=True)
        assert serializer.is_valid()
        updated_user = serializer.save()

        assert updated_user.username == new_data["username"]
        assert updated_user.email == new_data["email"]


@pytest.mark.django_db
class TestRegisterSerializer:
    """Tests for RegisterSerializer behavior"""

    def test_register_serializer_password_write_only(self):
        """Password field is write-only"""
        user_data = {
            "username": "testuser",
            "password": "SecurePass123!",
            "email": "test@example.com",
        }

        serializer = RegisterSerializer(data=user_data)
        assert serializer.is_valid()

        # Password should not be in serialized data
        assert "password" not in serializer.data

    def test_register_serializer_create_hashes_password(self):
        """RegisterSerializer.create properly hashes password"""
        user_data = {
            "username": "passuser",
            "password": "PlainTextPass123!",
            "email": "pass@example.com",
        }

        serializer = RegisterSerializer(data=user_data)
        assert serializer.is_valid()
        user = serializer.save()

        # Password should be hashed, not plain text
        assert user.password != "PlainTextPass123!"
        # But it should be able to authenticate with the plain password
        assert user.check_password("PlainTextPass123!")

    def test_register_serializer_required_fields(self):
        """RegisterSerializer requires all necessary fields"""
        serializer = RegisterSerializer(data={})
        assert not serializer.is_valid()
        assert "username" in serializer.errors
        assert "password" in serializer.errors
        # Email is not required (allow_blank=True)

    def test_register_serializer_read_only_fields(self):
        """read_only fields are not accepted in input"""
        user_data = {
            "username": "rouser",
            "password": "SecurePass123!",
            "email": "ro@example.com",
            "id": 99999,
            "date_joined": "2020-01-01",
        }

        serializer = RegisterSerializer(data=user_data)
        assert serializer.is_valid()
        assert "id" not in serializer.validated_data
        assert "date_joined" not in serializer.validated_data

    def test_register_serializer_returns_all_fields(self):
        """RegisterSerializer returns appropriate fields in response"""
        user_data = {
            "username": "respuser",
            "password": "SecurePass123!",
            "email": "resp@example.com",
        }

        serializer = RegisterSerializer(data=user_data)
        assert serializer.is_valid()
        user = serializer.save()

        # After save, check the response would have these fields
        response_serializer = RegisterSerializer(user)
        assert "id" in response_serializer.data
        assert "username" in response_serializer.data
        assert "email" in response_serializer.data
        assert "date_joined" in response_serializer.data
        # Password should still not be in response
        assert "password" not in response_serializer.data


@pytest.mark.django_db
class TestUserProfilePhoto:
    """Tests for user profile photo functionality"""

    def test_update_user_photo(self, admin_client, users_list, sample_image):
        """Admin can update user's photo"""
        user = users_list["recipe_owner_user"]
        response = admin_client.patch(
            f"{ENDPOINT}{user.id}/",
            {"photo": sample_image},
            format="multipart",
        )

        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.photo is not None

    def test_me_update_photo(self, authenticated_client, sample_image):
        """Authenticated user can update their own photo"""
        response = authenticated_client.patch(
            f"{ENDPOINT}me/",
            {"photo": sample_image},
            format="multipart",
        )

        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestUserDateOfBirth:
    """Tests for user date of birth field"""

    def test_set_date_of_birth(self, admin_client, users_list):
        """Admin can set user's date of birth"""
        user = users_list["recipe_owner_user"]
        birth_date = "1990-05-15"
        response = admin_client.patch(
            f"{ENDPOINT}{user.id}/",
            {"date_of_birth": birth_date},
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["date_of_birth"] == birth_date

        user.refresh_from_db()
        assert str(user.date_of_birth) == birth_date

    def test_user_can_set_own_date_of_birth(self, authenticated_client):
        """User can set their own date of birth via /me"""
        birth_date = "1995-10-20"
        response = authenticated_client.patch(
            f"{ENDPOINT}me/",
            {"date_of_birth": birth_date},
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["date_of_birth"] == birth_date

    def test_clear_date_of_birth(self, admin_client, users_list):
        """Admin can clear user's date of birth"""
        user = users_list["recipe_owner_user"]
        user.date_of_birth = "1990-05-15"
        user.save()

        response = admin_client.patch(
            f"{ENDPOINT}{user.id}/",
            {"date_of_birth": None},
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["date_of_birth"] is None

        user.refresh_from_db()
        assert user.date_of_birth is None


@pytest.mark.django_db
class TestUserFieldValidation:
    """Tests for user field validation"""

    def test_username_max_length(self, admin_client, users_list):
        """Username field respects max length"""
        user = users_list["recipe_owner_user"]
        long_username = "a" * 151  # Max is 150
        response = admin_client.patch(
            f"{ENDPOINT}{user.id}/",
            {"username": long_username},
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "username" in response.data

    def test_invalid_email_format(self, admin_client, users_list):
        """Invalid email format is rejected"""
        user = users_list["recipe_owner_user"]
        response = admin_client.patch(
            f"{ENDPOINT}{user.id}/",
            {"email": "not-an-email"},
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.data
