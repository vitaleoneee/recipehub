from unittest.mock import patch

import pytest
from django.urls import reverse

from recipehub.factories import RecipeFactory


@pytest.mark.django_db
def test_review_creates_redis_rating(client, users_list, fake_redis):
    with patch("recipehub.apps.reviews.views.r", fake_redis):
        first_user = users_list["first_simple_user"]
        recipe = RecipeFactory.create(user=first_user, slug="fish")
        client.force_login(first_user)

        response = client.post(
            reverse("reviews:create-review"),
            data={"slug": recipe.slug, "rating": 3},
            content_type="application/json",
        )

        assert response.status_code == 200

        key = "recipe:ratings"

        assert fake_redis.exists(key) == 1

        members = fake_redis.zrange(key, 0, -1)
        members = [int(m) for m in members]

        assert recipe.id in members

        score = fake_redis.zscore(key, recipe.id)
        assert score is not None
