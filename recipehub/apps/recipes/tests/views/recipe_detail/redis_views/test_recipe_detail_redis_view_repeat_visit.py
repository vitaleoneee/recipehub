from unittest.mock import patch

import pytest
from django.urls import reverse
from pytest_django.asserts import assertContains
from recipehub.factories import RecipeFactory


@pytest.mark.django_db()
class TestRecipeDetailRedisViewRepeatVisit:
    """Tests repeat visits view counting logic"""

    def test_recipe_detail_repeat_visit(self, client, users_list, fake_redis):
        with patch("recipehub.apps.recipes.views.r", fake_redis):
            recipe = RecipeFactory.create(slug="fish", moderation_status="approved")
            user = users_list["first_simple_user"]

            # First visit
            client.force_login(user)
            client.get(reverse("recipes:recipe-detail", kwargs={"slug": recipe.slug}))

            redis_key = f"user:{user.id}:recipe:{recipe.id}:view"
            assert int(fake_redis.get(redis_key) or 0) == 1

            # Second visit
            response = client.get(
                reverse("recipes:recipe-detail", kwargs={"slug": recipe.slug})
            )

            redis_key = f"user:{user.id}:recipe:{recipe.id}:view"
            assert int(fake_redis.get(redis_key) or 0) == 1

            assertContains(response, "1 views")
