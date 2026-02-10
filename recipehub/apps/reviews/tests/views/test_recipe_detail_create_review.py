import pytest
import json
from django.urls import reverse
from recipehub.factories import RecipeFactory


@pytest.mark.django_db
class TestRecipeReviews:
    """Tests for creating and updating reviews via views"""

    def test_review_get_not_allowed(self, client, users_list):
        """GET to create-review should return 405"""
        # Testing GET request returns 405
        first_user = users_list["first_simple_user"]
        client.force_login(first_user)
        response = client.get(reverse("reviews:create-review"))
        assert response.status_code == 405

    def test_review_post_missing_fields(self, client, users_list):
        """POST without required fields returns 400"""
        first_user = users_list["first_simple_user"]
        client.force_login(first_user)

        # Missing slug
        response = client.post(
            reverse("reviews:create-review"),
            data={"rating": 3},
            content_type="application/json",
        )
        assert response.status_code == 400

        # Missing rating
        response = client.post(
            reverse("reviews:create-review"),
            data={"slug": "fish"},
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_review_post_create(self, client, users_list):
        """Create a new review for a recipe"""
        recipe_owner_user = users_list["recipe_owner_user"]
        first_user = users_list["first_simple_user"]
        client.force_login(first_user)

        recipe = RecipeFactory.create(
            user=recipe_owner_user, slug="fish", moderation_status="approved"
        )

        # Sending valid POST request
        response = client.post(
            reverse("reviews:create-review"),
            data=json.dumps({"rating": 3, "slug": recipe.slug}),
            content_type="application/json",
        )
        data = response.json()

        assert response.status_code == 200
        assert data["status"] == "ok"
        assert data["rating"] == 3
        assert data["updated"] is False
        assert data["average_rating"] == 3

    def test_review_post_update(self, client, users_list):
        """Updating an existing review replaces old rating"""
        recipe_owner_user = users_list["recipe_owner_user"]
        first_user = users_list["first_simple_user"]
        client.force_login(first_user)

        recipe = RecipeFactory.create(
            user=recipe_owner_user, slug="fish", moderation_status="approved"
        )

        # Creating initial review
        client.post(
            reverse("reviews:create-review"),
            data=json.dumps({"rating": 3, "slug": recipe.slug}),
            content_type="application/json",
        )

        # Updating review
        response = client.post(
            reverse("reviews:create-review"),
            data=json.dumps({"rating": 5, "slug": recipe.slug}),
            content_type="application/json",
        )
        data = response.json()

        assert response.status_code == 200
        assert data["status"] == "ok"
        assert data["rating"] == 5
        assert data["updated"] is True
        assert data["average_rating"] == 5

    def test_review_average_rating(self, client, users_list):
        """Average rating should be calculated across multiple reviews"""
        recipe_owner_user = users_list["recipe_owner_user"]
        first_user = users_list["first_simple_user"]
        second_user = users_list["second_simple_user"]

        client.force_login(first_user)
        recipe = RecipeFactory.create(
            user=recipe_owner_user, slug="fish", moderation_status="approved"
        )

        # First user adds a review
        client.post(
            reverse("reviews:create-review"),
            data=json.dumps({"rating": 5, "slug": recipe.slug}),
            content_type="application/json",
        )

        # Second user adds a review
        client.force_login(second_user)
        response = client.post(
            reverse("reviews:create-review"),
            data=json.dumps({"rating": 2, "slug": recipe.slug}),
            content_type="application/json",
        )
        data = response.json()

        assert response.status_code == 200
        assert data["status"] == "ok"
        assert data["rating"] == 2
        assert data["updated"] is False
        # Testing average rating
        assert data["average_rating"] == pytest.approx(3.5)
