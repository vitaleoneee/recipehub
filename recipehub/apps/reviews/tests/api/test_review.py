import pytest
from rest_framework import status

from recipehub.apps.reviews.models import Review
from recipehub.apps.recipes.api.serializers import RecipeSerializer
from recipehub.factories import ReviewFactory, RecipeFactory

ENDPOINT = "/api/reviews/"


@pytest.mark.django_db
class TestReviewPermissions:
    """Permissions rights check tests for review operations"""

    @pytest.mark.parametrize(
        "client_fixture,expected_status",
        [
            ("api_client", status.HTTP_401_UNAUTHORIZED),
            ("authenticated_client", status.HTTP_200_OK),
            ("admin_client", status.HTTP_200_OK),
        ],
    )
    def test_list_permissions(self, client_fixture, expected_status, review, request):
        """Only admins can list all reviews"""
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
        self, client_fixture, expected_status, review_data, request
    ):
        """Only authenticated users can create reviews"""
        client = request.getfixturevalue(client_fixture)
        response = client.post(ENDPOINT, data=review_data, format="json")
        assert response.status_code == expected_status

    @pytest.mark.parametrize(
        "client_fixture,expected_status",
        [
            ("api_client", status.HTTP_401_UNAUTHORIZED),
            ("authenticated_client", status.HTTP_403_FORBIDDEN),
            ("review_owner_client", status.HTTP_200_OK),
            ("admin_client", status.HTTP_200_OK),
        ],
    )
    def test_update_permissions(
        self, client_fixture, expected_status, review, review_data, request
    ):
        """Only review owner and admin can update"""
        client = request.getfixturevalue(client_fixture)
        response = client.put(f"{ENDPOINT}{review.id}/", review_data, format="json")
        assert response.status_code == expected_status

    @pytest.mark.parametrize(
        "client_fixture,expected_status",
        [
            ("api_client", status.HTTP_401_UNAUTHORIZED),
            ("authenticated_client", status.HTTP_403_FORBIDDEN),
            ("review_owner_client", status.HTTP_200_OK),
            ("admin_client", status.HTTP_200_OK),
        ],
    )
    def test_patch_permissions(self, client_fixture, expected_status, review, request):
        """Only review owner and admin can partial update"""
        client = request.getfixturevalue(client_fixture)
        response = client.patch(
            f"{ENDPOINT}{review.id}/",
            {"rating": 4},
            format="json",
        )
        assert response.status_code == expected_status

    @pytest.mark.parametrize(
        "client_fixture,expected_status",
        [
            ("api_client", status.HTTP_401_UNAUTHORIZED),
            ("authenticated_client", status.HTTP_403_FORBIDDEN),
            ("review_owner_client", status.HTTP_204_NO_CONTENT),
            ("admin_client", status.HTTP_204_NO_CONTENT),
        ],
    )
    def test_delete_permissions(self, client_fixture, expected_status, review, request):
        """Only review owner and admin can delete"""
        client = request.getfixturevalue(client_fixture)
        response = client.delete(f"{ENDPOINT}{review.id}/")
        assert response.status_code == expected_status


@pytest.mark.django_db
class TestReviewUpdateByRecipePermissions:
    """Permissions tests for update_by_recipe custom action"""

    @pytest.mark.parametrize(
        "client_fixture,expected_status",
        [
            ("api_client", status.HTTP_401_UNAUTHORIZED),
            ("authenticated_client", status.HTTP_403_FORBIDDEN),
            ("review_owner_client", status.HTTP_200_OK),
            ("admin_client", status.HTTP_200_OK),
        ],
    )
    def test_update_by_recipe_put_permissions(
        self, client_fixture, expected_status, review, review_data, request
    ):
        """Only review owner and admin can PUT update_by_recipe"""
        client = request.getfixturevalue(client_fixture)
        response = client.put(
            f"{ENDPOINT}recipes/{review.recipe.id}/",
            review_data,
            format="json",
        )
        assert response.status_code == expected_status

    @pytest.mark.parametrize(
        "client_fixture,expected_status",
        [
            ("api_client", status.HTTP_401_UNAUTHORIZED),
            ("authenticated_client", status.HTTP_403_FORBIDDEN),
            ("review_owner_client", status.HTTP_200_OK),
            ("admin_client", status.HTTP_200_OK),
        ],
    )
    def test_update_by_recipe_patch_permissions(
        self, client_fixture, expected_status, review, request
    ):
        """Only review owner and admin can PATCH update_by_recipe"""
        client = request.getfixturevalue(client_fixture)
        response = client.patch(
            f"{ENDPOINT}recipes/{review.recipe.id}/",
            {"rating": 4},
            format="json",
        )
        assert response.status_code == expected_status


@pytest.mark.django_db
class TestDefaultUserReviewOperations:
    def test_create_review(self, authenticated_client, review_data):
        """User can create a review"""
        response = authenticated_client.post(ENDPOINT, review_data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["rating"] == review_data["rating"]
        assert Review.objects.filter(rating=review_data["rating"]).exists()

    def test_create_review_sets_user(self, authenticated_client, review_data):
        """Creating review automatically sets current user"""
        response = authenticated_client.post(ENDPOINT, review_data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        review_id = response.data.get("id") if isinstance(response.data, dict) else None
        if review_id is None:
            review = Review.objects.filter(
                rating=review_data["rating"],
                user=authenticated_client.handler._force_user,
            ).first()
        else:
            review = Review.objects.get(id=review_id)

        assert str(review.user) == str(authenticated_client.handler._force_user)

    def test_create_review_invalid_data(self, authenticated_client, recipe):
        """Invalid review data returns 400"""
        response = authenticated_client.post(
            ENDPOINT, {"recipe": recipe.id}, format="json"
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_review_own_recipe_validation(
        self, authenticated_client, users_list
    ):
        """User cannot review their own recipe"""
        user = users_list["first_simple_user"]
        recipe = RecipeFactory(user=user, moderation_status="approved")

        review_data = {"recipe": recipe.id, "rating": 5}
        response = authenticated_client.post(ENDPOINT, review_data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        errors = str(response.data).lower()
        assert "yourself" in errors

    def test_list_shows_only_own_reviews(self, authenticated_client, users_list):
        """Authenticated user only sees their own reviews in list"""
        user = users_list["first_simple_user"]

        recipes = RecipeFactory.create_batch(3, moderation_status="approved")
        for r in recipes:
            ReviewFactory(user=user, recipe=r)

        other_user = users_list["second_simple_user"]
        other_recipes = RecipeFactory.create_batch(2, moderation_status="approved")
        for r in other_recipes:
            ReviewFactory(user=other_user, recipe=r)

        response = authenticated_client.get(ENDPOINT)

        assert response.status_code == status.HTTP_200_OK
        data = (
            response.data.get("results")
            if isinstance(response.data, dict) and "results" in response.data
            else response.data
        )
        assert len(data) == 3
        assert all(item["user"] == str(user) for item in data)

    def test_update_owned_review(self, review_owner_client, review, review_data):
        """User can update their own review"""
        review_data["rating"] = 4
        response = review_owner_client.put(
            f"{ENDPOINT}{review.id}/", review_data, format="json"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["rating"] == review_data["rating"]

        review.refresh_from_db()
        assert review.rating == review_data["rating"]

    def test_update_not_owned_review(self, authenticated_client, review, review_data):
        """User cannot update another user's review"""
        original_rating = review.rating
        review_data["rating"] = 4
        response = authenticated_client.put(
            f"{ENDPOINT}{review.id}/", review_data, format="json"
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

        review.refresh_from_db()
        assert review.rating == original_rating

    def test_partial_update_owned_review(self, review_owner_client, review):
        """User can partially update their own review"""
        new_rating = 4
        response = review_owner_client.patch(
            f"{ENDPOINT}{review.id}/", {"rating": new_rating}, format="json"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["rating"] == new_rating

        review.refresh_from_db()
        assert review.rating == new_rating

    def test_partial_update_not_owned_review(self, authenticated_client, review):
        """User cannot partially update another user's review"""
        original_rating = review.rating
        response = authenticated_client.patch(
            f"{ENDPOINT}{review.id}/", {"rating": 4}, format="json"
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

        review.refresh_from_db()
        assert review.rating == original_rating

    def test_delete_owned_review(self, review_owner_client, review):
        """User can delete their own review"""
        review_id = review.id
        response = review_owner_client.delete(f"{ENDPOINT}{review.id}/")

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Review.objects.filter(id=review_id).exists()

    def test_delete_not_owned_review(self, authenticated_client, review):
        """User cannot delete another user's review"""
        review_id = review.id
        response = authenticated_client.delete(f"{ENDPOINT}{review.id}/")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Review.objects.filter(id=review_id).exists()


@pytest.mark.django_db
class TestReviewUpdateByRecipeAction:
    """Tests for update_by_recipe custom action"""

    def test_update_by_recipe_put_owned_review(
        self, review_owner_client, review, review_data
    ):
        """User can PUT update their own review by recipe ID"""
        review_data["rating"] = 4
        response = review_owner_client.put(
            f"{ENDPOINT}recipes/{review.recipe.id}/",
            review_data,
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["rating"] == review_data["rating"]

        review.refresh_from_db()
        assert review.rating == review_data["rating"]

    def test_update_by_recipe_patch_owned_review(self, review_owner_client, review):
        """User can PATCH update their own review by recipe ID"""
        new_rating = 3
        response = review_owner_client.patch(
            f"{ENDPOINT}recipes/{review.recipe.id}/",
            {"rating": new_rating},
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["rating"] == new_rating

        review.refresh_from_db()
        assert review.rating == new_rating

    def test_update_by_recipe_not_owned_review(
        self, authenticated_client, review, review_data
    ):
        """User cannot update another user's review by recipe ID"""
        original_rating = review.rating
        review_data["rating"] = 4
        response = authenticated_client.put(
            f"{ENDPOINT}recipes/{review.recipe.id}/",
            review_data,
            format="json",
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

        review.refresh_from_db()
        assert review.rating == original_rating

    def test_update_by_recipe_admin_can_update_any(
        self, admin_client, review, review_data
    ):
        """Admin can update any review by recipe ID"""
        review_data["rating"] = 4
        response = admin_client.put(
            f"{ENDPOINT}recipes/{review.recipe.id}/",
            review_data,
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["rating"] == review_data["rating"]

        review.refresh_from_db()
        assert review.rating == review_data["rating"]

    def test_update_by_recipe_not_found(self, review_owner_client):
        """Returns 404 when review not found for recipe"""
        response = review_owner_client.put(
            f"{ENDPOINT}recipes/99999/",
            {"rating": 5},
            format="json",
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Review not found" in response.data["detail"]

    def test_update_by_recipe_unauthenticated(self, api_client, review, review_data):
        """Unauthenticated user cannot update review by recipe ID"""
        response = api_client.put(
            f"{ENDPOINT}recipes/{review.recipe.id}/",
            review_data,
            format="json",
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestAdminUserReviewOperations:
    def test_admin_list_all_reviews(self, admin_client, reviews_fixture):
        """Admin can list all reviews"""
        response = admin_client.get(ENDPOINT)

        assert response.status_code == status.HTTP_200_OK
        data = (
            response.data.get("results")
            if isinstance(response.data, dict) and "results" in response.data
            else response.data
        )
        assert len(data) == len(reviews_fixture["all_reviews"])

    def test_admin_create_review(self, admin_client, review_data):
        """Admin can create a review"""
        response = admin_client.post(ENDPOINT, review_data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["rating"] == review_data["rating"]
        assert Review.objects.filter(rating=review_data["rating"]).exists()

    def test_admin_update_any_review(self, admin_client, review, review_data):
        """Admin can update any review"""
        review_data["rating"] = 4
        response = admin_client.put(
            f"{ENDPOINT}{review.id}/", review_data, format="json"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["rating"] == review_data["rating"]

        review.refresh_from_db()
        assert review.rating == review_data["rating"]

    def test_admin_partial_update_any_review(self, admin_client, review):
        """Admin can partially update any review"""
        new_rating = 4
        response = admin_client.patch(
            f"{ENDPOINT}{review.id}/", {"rating": new_rating}, format="json"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["rating"] == new_rating

        review.refresh_from_db()
        assert review.rating == new_rating

    def test_admin_delete_any_review(self, admin_client, review):
        """Admin can delete any review"""
        review_id = review.id
        response = admin_client.delete(f"{ENDPOINT}{review.id}/")

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Review.objects.filter(id=review_id).exists()


@pytest.mark.django_db
class TestRecipeSerializerBehavior:
    """Tests for RecipeSerializer behavior (replaced ReviewSerializer tests)"""

    @pytest.mark.parametrize(
        "field,value",
        [
            ("user", 1),
            ("created_at", "2026-01-01"),
            ("slug", "forced-slug"),
        ],
    )
    def test_read_only_fields(self, field, value, recipe_serializer_data):
        """Read-only fields should be ignored during create"""
        recipe_serializer_data[field] = value

        serializer = RecipeSerializer(data=recipe_serializer_data)

        assert serializer.is_valid(), serializer.errors
        assert field not in serializer.validated_data

    def test_create_sets_user(
        self, recipe_serializer_data, authenticated_client, api_rf
    ):
        """Create method should set user from request context"""
        request = api_rf.post("/recipes/")
        request.user = authenticated_client.handler._force_user

        serializer = RecipeSerializer(
            data=recipe_serializer_data, context={"request": request}
        )

        assert serializer.is_valid(), serializer.errors

        recipe = serializer.save()

        assert recipe.user == authenticated_client.handler._force_user

    def test_user_is_string_related(self, recipe):
        """User field should be StringRelatedField in output"""
        serializer = RecipeSerializer(recipe)

        assert serializer.data["user"] == str(recipe.user)

    def test_validate_ingredients_format_valid(self, recipe_serializer_data):
        """Valid ingredients format passes validation"""
        recipe_serializer_data["ingredients"] = "sugar - 1tbsp"
        serializer = RecipeSerializer(data=recipe_serializer_data)
        assert serializer.is_valid(), serializer.errors

    def test_validate_ingredients_format_invalid(self, recipe_serializer_data):
        """Invalid ingredients format fails validation"""
        recipe_serializer_data["ingredients"] = "invalid format"
        serializer = RecipeSerializer(data=recipe_serializer_data)
        assert not serializer.is_valid()
        assert "ingredients" in serializer.errors

    def test_required_fields(self, recipe_serializer_data):
        """Missing required fields cause validation error"""
        if "name" in recipe_serializer_data:
            del recipe_serializer_data["name"]
        serializer = RecipeSerializer(data=recipe_serializer_data)
        assert not serializer.is_valid()
        assert "name" in serializer.errors

    def test_fields_in_output(self, recipe):
        """Serializer output includes expected fields"""
        serializer = RecipeSerializer(recipe)
        assert "created_at" in serializer.data
        assert "slug" in serializer.data
