import json

import pytest
from django.urls import reverse

from recipehub.factories import RecipeFactory, UserRecipeFavoriteFactory


@pytest.mark.django_db
class TestUserViews:
    """Tests for users views: profile, saved_recipes, remove_saved_recipe"""

    def test_profile_requires_login(self, client):
        response = client.get(reverse("profile"))
        assert response.status_code == 302

    def test_profile_shows_pending_recipes(self, client, users_list):
        user = users_list["first_simple_user"]
        client.force_login(user)
        # create a pending recipe
        RecipeFactory.create(user=user, moderation_status="in_process")
        response = client.get(reverse("profile"))
        assert response.status_code == 200
        assert "pending_recipes" in response.context

    def test_saved_recipes_requires_login(self, client):
        response = client.get(reverse("saved-recipes"))
        assert response.status_code == 302

    def test_saved_recipes_shows_saved(self, client, users_list):
        user = users_list["first_simple_user"]
        client.force_login(user)
        recipe = RecipeFactory.create(user=user)
        UserRecipeFavoriteFactory.create(user=user, recipe=recipe)
        response = client.get(reverse("saved-recipes"))
        assert response.status_code == 200
        assert "saved_recipes" in response.context

    def test_remove_saved_recipe_requires_post(self, client, users_list):
        user = users_list["first_simple_user"]
        client.force_login(user)
        response = client.get(reverse("remove_saved_recipe"))
        assert response.status_code == 405

    def test_remove_saved_recipe_invalid_json(self, client, users_list):
        user = users_list["first_simple_user"]
        client.force_login(user)
        response = client.post(
            reverse("remove_saved_recipe"),
            data="not-json",
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_remove_saved_recipe_missing_slug(self, client, users_list):
        user = users_list["first_simple_user"]
        client.force_login(user)
        response = client.post(
            reverse("remove_saved_recipe"),
            data=json.dumps({}),
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_remove_saved_recipe_not_found(self, client, users_list):
        user = users_list["first_simple_user"]
        client.force_login(user)
        response = client.post(
            reverse("remove_saved_recipe"),
            data=json.dumps({"slug": "no-exist"}),
            content_type="application/json",
        )
        assert response.status_code == 404

    def test_remove_saved_recipe_success(self, client, users_list):
        user = users_list["first_simple_user"]
        client.force_login(user)
        recipe = RecipeFactory.create(user=user, slug="fish")
        UserRecipeFavoriteFactory.create(user=user, recipe=recipe)

        response = client.post(
            reverse("remove_saved_recipe"),
            data=json.dumps({"slug": recipe.slug}),
            content_type="application/json",
        )
        assert response.status_code == 200
        assert response.json()["removed"] is True
