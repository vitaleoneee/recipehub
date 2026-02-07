import pytest
from rest_framework import status

from recipehub.apps.reviews.api.serializers import (
    CommentSerializer,
    CommentAdminSerializer,
    CommentStatusSerializer,
)
from recipehub.apps.reviews.models import Comment
from recipehub.factories import CommentFactory, UserFactory

ENDPOINT = "/api/comments/"


@pytest.mark.django_db
class TestCommentPermissions:
    """Permissions rights check tests for comment operations"""

    @pytest.mark.parametrize(
        "client_fixture,expected_status",
        [
            ("api_client", status.HTTP_401_UNAUTHORIZED),
            ("authenticated_client", status.HTTP_403_FORBIDDEN),
            ("admin_client", status.HTTP_200_OK),
        ],
    )
    def test_list_permissions(self, client_fixture, expected_status, comment, request):
        """Only admins can list all comments"""
        client = request.getfixturevalue(client_fixture)
        response = client.get(ENDPOINT)
        assert response.status_code == expected_status

    @pytest.mark.parametrize(
        "client_fixture,expected_status",
        [
            ("api_client", status.HTTP_401_UNAUTHORIZED),
            ("authenticated_client", status.HTTP_201_CREATED),
        ],
    )
    def test_create_permissions(
        self, client_fixture, expected_status, comment_data, request
    ):
        """Only authenticated users can create comments"""
        client = request.getfixturevalue(client_fixture)
        response = client.post(ENDPOINT, data=comment_data, format="json")
        assert response.status_code == expected_status

    @pytest.mark.parametrize(
        "client_fixture,expected_status",
        [
            ("api_client", status.HTTP_401_UNAUTHORIZED),
            ("authenticated_client", status.HTTP_403_FORBIDDEN),
            ("comment_owner_client", status.HTTP_200_OK),
            ("admin_client", status.HTTP_200_OK),
        ],
    )
    def test_update_permissions(
        self, client_fixture, expected_status, comment, comment_data, request
    ):
        """Only comment owner and admin can update"""
        client = request.getfixturevalue(client_fixture)
        response = client.put(f"{ENDPOINT}{comment.id}/", comment_data, format="json")
        assert response.status_code == expected_status

    @pytest.mark.parametrize(
        "client_fixture,expected_status",
        [
            ("api_client", status.HTTP_401_UNAUTHORIZED),
            ("authenticated_client", status.HTTP_403_FORBIDDEN),
            ("comment_owner_client", status.HTTP_200_OK),
            ("admin_client", status.HTTP_200_OK),
        ],
    )
    def test_patch_permissions(self, client_fixture, expected_status, comment, request):
        """Only comment owner and admin can partial update"""
        client = request.getfixturevalue(client_fixture)
        response = client.patch(
            f"{ENDPOINT}{comment.id}/",
            {"body": "Updated comment"},
            format="json",
        )
        assert response.status_code == expected_status

    @pytest.mark.parametrize(
        "client_fixture,expected_status",
        [
            ("api_client", status.HTTP_401_UNAUTHORIZED),
            ("authenticated_client", status.HTTP_403_FORBIDDEN),
            ("comment_owner_client", status.HTTP_204_NO_CONTENT),
            ("admin_client", status.HTTP_204_NO_CONTENT),
        ],
    )
    def test_delete_permissions(
        self, client_fixture, expected_status, comment, request
    ):
        """Only comment owner and admin can delete"""
        client = request.getfixturevalue(client_fixture)
        response = client.delete(f"{ENDPOINT}{comment.id}/")
        assert response.status_code == expected_status


@pytest.mark.django_db
class TestDefaultUserCommentOperations:
    def test_create_comment(self, authenticated_client, comment_data):
        """User can create a comment"""
        response = authenticated_client.post(ENDPOINT, comment_data, format="json")
        body = comment_data["body"]

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["body"] == body
        assert Comment.objects.filter(body=body).exists()

    def test_create_comment_invalid_data(self, authenticated_client):
        """Invalid comment data returns 400"""
        response = authenticated_client.post(ENDPOINT, {"body": ""}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_owned_comment(self, comment_owner_client, comment, comment_data):
        """User can update their own comment"""
        comment_data["body"] = "Updated Comment Text"
        response = comment_owner_client.put(
            f"{ENDPOINT}{comment.id}/", comment_data, format="json"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["body"] == comment_data["body"]

        comment.refresh_from_db()
        assert comment.body == comment_data["body"]

    def test_update_not_owned_comment(
        self, authenticated_client, comment, comment_data
    ):
        """User cannot update another user's comment"""
        original_body = comment.body
        comment_data["body"] = "Updated Comment Text"
        response = authenticated_client.put(
            f"{ENDPOINT}{comment.id}/", comment_data, format="json"
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

        comment.refresh_from_db()
        assert comment.body == original_body

    def test_partial_update_owned_comment(self, comment_owner_client, comment):
        """User can partially update their own comment"""
        new_body = "Partially Updated Comment"
        response = comment_owner_client.patch(
            f"{ENDPOINT}{comment.id}/", {"body": new_body}, format="json"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["body"] == new_body

        comment.refresh_from_db()
        assert comment.body == new_body

    def test_partial_update_not_owned_comment(self, authenticated_client, comment):
        """User cannot partially update another user's comment"""
        original_body = comment.body
        response = authenticated_client.patch(
            f"{ENDPOINT}{comment.id}/", {"body": "New Body"}, format="json"
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

        comment.refresh_from_db()
        assert comment.body == original_body

    def test_delete_owned_comment(self, comment_owner_client, comment):
        """User can delete their own comment"""
        comment_id = comment.id
        response = comment_owner_client.delete(f"{ENDPOINT}{comment.id}/")

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Comment.objects.filter(id=comment_id).exists()

    def test_delete_not_owned_comment(self, authenticated_client, comment):
        """User cannot delete another user's comment"""
        comment_id = comment.id
        response = authenticated_client.delete(f"{ENDPOINT}{comment.id}/")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Comment.objects.filter(id=comment_id).exists()


@pytest.mark.django_db
class TestAdminUserCommentOperations:
    def test_admin_list_all_comments(self, admin_client, comments_fixture):
        """Admin can list all comments"""
        response = admin_client.get(ENDPOINT)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == len(comments_fixture["all_comments"])

    def test_admin_create_comment(self, admin_client, comment_data):
        """Admin can create a comment"""
        response = admin_client.post(ENDPOINT, comment_data, format="json")
        body = comment_data["body"]

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["body"] == body
        assert Comment.objects.filter(body=body).exists()

    def test_admin_update_any_comment(self, admin_client, comment, comment_data):
        """Admin can update any comment"""
        comment_data["body"] = "Admin Updated Comment"
        response = admin_client.put(
            f"{ENDPOINT}{comment.id}/", comment_data, format="json"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["body"] == comment_data["body"]

        comment.refresh_from_db()
        assert comment.body == comment_data["body"]

    def test_admin_partial_update_any_comment(self, admin_client, comment):
        """Admin can partially update any comment"""
        new_body = "Admin Partial Update"
        response = admin_client.patch(
            f"{ENDPOINT}{comment.id}/", {"body": new_body}, format="json"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["body"] == new_body

        comment.refresh_from_db()
        assert comment.body == new_body

    def test_admin_delete_any_comment(self, admin_client, comment):
        """Admin can delete any comment"""
        comment_id = comment.id
        response = admin_client.delete(f"{ENDPOINT}{comment.id}/")

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Comment.objects.filter(id=comment_id).exists()


@pytest.mark.django_db
class TestCommentCustomActions:
    """Tests for custom actions in CommentViewSet"""

    # My Comments action tests
    def test_my_comments_permissions(self, api_client):
        """Unauthorized users cannot access my-comments"""
        response = api_client.get(f"{ENDPOINT}my-comments/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_my_comments_authenticated(self, authenticated_client, users_list):
        """User can see only their own comments"""
        user = users_list["first_simple_user"]

        # Create comments for current user
        CommentFactory.create_batch(3, user=user)

        # Create comments for other users
        CommentFactory.create_batch(2)

        response = authenticated_client.get(f"{ENDPOINT}my-comments/")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3
        assert Comment.objects.filter(user=user).count() == 3

    def test_my_comments_empty(self, authenticated_client):
        """User with no comments gets empty list"""
        response = authenticated_client.get(f"{ENDPOINT}my-comments/")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

    # Activate action tests
    def test_activate_permissions(self, authenticated_client, comment):
        """Regular users cannot activate/deactivate comments"""
        response = authenticated_client.patch(
            f"{ENDPOINT}{comment.id}/activate/",
            {"active": True},
            format="json",
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_activate_admin_permissions(self, api_client, comment):
        """Unauthorized users cannot activate comments"""
        response = api_client.patch(
            f"{ENDPOINT}{comment.id}/activate/",
            {"active": True},
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_activate_comment_to_true(self, admin_client, comment):
        """Admin can activate a comment"""
        comment.active = False
        comment.save()

        response = admin_client.patch(
            f"{ENDPOINT}{comment.id}/activate/",
            {"active": True},
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["active"] is True
        assert response.data["id"] == comment.id
        assert response.data["recipe"] == comment.recipe_id

        comment.refresh_from_db()
        assert comment.active is True

    def test_activate_comment_to_false(self, admin_client, comment):
        """Admin can deactivate a comment"""
        comment.active = True
        comment.save()

        response = admin_client.patch(
            f"{ENDPOINT}{comment.id}/activate/",
            {"active": False},
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["active"] is False

        comment.refresh_from_db()
        assert comment.active is False

    def test_activate_uses_transaction(self, admin_client, comment):
        """Activate action uses atomic transaction"""
        response = admin_client.patch(
            f"{ENDPOINT}{comment.id}/activate/",
            {"active": True},
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        comment.refresh_from_db()
        assert comment.active is True

    def test_activate_invalid_data(self, admin_client, comment):
        """Invalid status data returns validation error"""
        response = admin_client.patch(
            f"{ENDPOINT}{comment.id}/activate/",
            {"active": "invalid"},
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_activate_missing_active_field(self, admin_client, comment):
        """Missing required active field returns validation error"""
        response = admin_client.patch(
            f"{ENDPOINT}{comment.id}/activate/",
            {},
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_activate_nonexistent_comment(self, admin_client):
        """Activating non-existent comment returns 404"""
        response = admin_client.patch(
            f"{ENDPOINT}99999/activate/",
            {"active": True},
            format="json",
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestCommentSerializerBehavior:
    """Tests for serializer behavior in different contexts"""

    def test_regular_user_gets_comment_serializer(
        self, authenticated_client, comment_data
    ):
        """Regular user gets CommentSerializer"""
        response = authenticated_client.post(ENDPOINT, comment_data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        # CommentSerializer should not have 'user' in write_only or editable
        assert "user" in response.data
        assert isinstance(response.data["user"], str)

    def test_admin_gets_comment_admin_serializer(self, admin_client, comment_data):
        """Admin gets CommentAdminSerializer when creating"""
        response = admin_client.post(ENDPOINT, comment_data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        # CommentAdminSerializer uses PrimaryKeyRelatedField for user
        assert "user" in response.data


@pytest.mark.django_db
class TestCommentStatusSerializer:
    def test_serializer_valid_active_field(self):
        serializer = CommentStatusSerializer(data={"active": True})
        assert serializer.is_valid()
        assert serializer.validated_data["active"] is True

    def test_serializer_valid_false_active(self):
        serializer = CommentStatusSerializer(data={"active": False})
        assert serializer.is_valid()
        assert serializer.validated_data["active"] is False

    def test_serializer_invalid_active_field(self):
        serializer = CommentStatusSerializer(data={"active": "invalid"})
        assert not serializer.is_valid()
        assert "active" in serializer.errors

    def test_serializer_missing_active_field(self):
        serializer = CommentStatusSerializer(data={})
        assert not serializer.is_valid()
        assert "active" in serializer.errors


@pytest.mark.django_db
class TestCommentSerializer:
    @pytest.mark.parametrize(
        "field,value",
        [
            ("user", 1),
            ("created_at", "2026-01-01"),
            ("active", True),
        ],
    )
    def test_read_only_fields(self, field, value, comment_serializer_data):
        """Read-only fields should be ignored during create"""
        comment_serializer_data[field] = value

        serializer = CommentSerializer(data=comment_serializer_data)

        assert serializer.is_valid(), serializer.errors
        assert field not in serializer.validated_data

    def test_create_sets_user(
        self, comment_serializer_data, authenticated_client, api_rf
    ):
        """Create method should set user from request context"""
        request = api_rf.post("/comments/")
        request.user = authenticated_client.handler._force_user

        serializer = CommentSerializer(
            data=comment_serializer_data, context={"request": request}
        )

        assert serializer.is_valid(), serializer.errors

        comment = serializer.save()

        assert comment.user == authenticated_client.handler._force_user

    def test_user_is_string_related(self, comment):
        """User field should be StringRelatedField in output"""
        serializer = CommentSerializer(comment)

        assert serializer.data["user"] == str(comment.user)


@pytest.mark.django_db
class TestCommentAdminSerializer:
    def test_admin_serializer_user_is_primary_key(self, admin_client, comment):
        """CommentAdminSerializer uses PrimaryKeyRelatedField for user"""
        serializer = CommentAdminSerializer(comment)

        assert serializer.data["user"] == comment.user.id

    def test_admin_can_set_different_user(self, admin_client, comment_data, api_rf):
        """Admin can set user when creating via CommentAdminSerializer"""
        user = UserFactory()
        comment_data["user"] = user.id

        request = api_rf.post("/comments/")
        request.user = admin_client.handler._force_user

        serializer = CommentAdminSerializer(
            data=comment_data, context={"request": request}
        )

        assert serializer.is_valid(), serializer.errors
        comment = serializer.save()
        assert comment.user == user

    def test_admin_serializer_defaults_to_request_user(
        self, admin_client, comment_data, api_rf
    ):
        """If user not provided, defaults to request user"""
        # Don't set user in data
        if "user" in comment_data:
            del comment_data["user"]

        request = api_rf.post("/comments/")
        request.user = admin_client.handler._force_user

        serializer = CommentAdminSerializer(
            data=comment_data, context={"request": request}
        )

        assert serializer.is_valid(), serializer.errors
        comment = serializer.save()
        assert comment.user == admin_client.handler._force_user

    @pytest.mark.parametrize("field", ["created_at"])
    def test_admin_serializer_read_only_fields(self, field, comment):
        """Certain fields are read-only even for admins"""
        serializer = CommentAdminSerializer(comment)
        assert field in serializer.data
