from unittest.mock import patch

import pytest
from django.urls import reverse
from pytest_django.asserts import assertContains

from recipehub.factories import RecipeFactory


@pytest.mark.django_db
def test_recipe_detail_redis_view(client, users_list, fake_redis):
    with patch("recipehub.apps.recipes.views.r", fake_redis):
        recipe = RecipeFactory.create(slug="fish", moderation_status="approved")
        user = users_list["first_simple_user"]

        client.force_login(user)
        response = client.get(
            reverse("recipes:recipe-detail", kwargs={"slug": recipe.slug})
        )
        redis_key = f"recipe:{recipe.id}:views"
        assert int(fake_redis.get(redis_key) or 0) == 1

        assertContains(response, "1 views")
