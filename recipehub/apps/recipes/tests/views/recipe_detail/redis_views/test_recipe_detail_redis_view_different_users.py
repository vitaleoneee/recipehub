from unittest.mock import patch

import pytest
from django.urls import reverse
from pytest_django.asserts import assertContains

from recipehub.factories import RecipeFactory


@pytest.mark.django_db()
def test_recipe_detail_redis_view_different_users(client, users_list, fake_redis):
    with patch("recipehub.apps.recipes.views.r", fake_redis):
        recipe = RecipeFactory.create(slug="fish", moderation_status="approved")
        first_user = users_list["first_simple_user"]
        second_user = users_list["second_simple_user"]

        # First user
        client.force_login(first_user)
        first_response = client.get(
            reverse("recipes:recipe-detail", kwargs={"slug": recipe.slug})
        )
        assertContains(first_response, "1 views")
        redis_key = f"recipe:{recipe.id}:views"
        assert int(fake_redis.get(redis_key) or 0) == 1

        # Second user
        client.force_login(second_user)
        second_response = client.get(
            reverse("recipes:recipe-detail", kwargs={"slug": recipe.slug})
        )
        assertContains(second_response, "2 views")
        assert int(fake_redis.get(redis_key) or 0) == 2
