import pytest
from pytest_django.asserts import assertContains, assertNotContains
from django.urls import reverse
from recipehub.factories import RecipeFactory, UserRecipeFavoriteFactory


@pytest.mark.django_db
def test_recipe_detail_favorite(client, users_list):
    # Testing favorite recipes display and owner restrictions
    recipe_owner_user, first_simple_user, second_simple_user, _ = users_list.values()

    recipe_from_owner_user = RecipeFactory.create(
        user=recipe_owner_user, slug="fish", moderation_status="approved"
    )
    recipe_from_another_user = RecipeFactory.create(
        user=first_simple_user, slug="pizza", moderation_status="approved"
    )
    recipe_from_second_user = RecipeFactory.create(
        user=second_simple_user, slug="borsh", moderation_status="approved"
    )

    UserRecipeFavoriteFactory.create(
        user=recipe_owner_user, recipe=recipe_from_another_user
    )

    client.force_login(recipe_owner_user)

    # Testing recipe already in favorites
    response = client.get(
        reverse("recipes:recipe-detail", kwargs={"slug": recipe_from_another_user.slug})
    )
    assert response.status_code == 200
    assertContains(response, "In Favorites")
    assert response.context["is_favorited"] is True

    # Testing recipe not in favorites
    response = client.get(
        reverse("recipes:recipe-detail", kwargs={"slug": recipe_from_second_user.slug})
    )
    assert response.status_code == 200
    assertContains(response, "Add to Favorites")

    # Testing owner cannot favorite their own recipe
    response = client.get(
        reverse("recipes:recipe-detail", kwargs={"slug": recipe_from_owner_user.slug})
    )
    assert response.status_code == 200
    assertNotContains(response, "Add to Favorites")
    assertNotContains(response, "In Favorites")
