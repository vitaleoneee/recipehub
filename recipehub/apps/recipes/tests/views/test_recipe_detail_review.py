import pytest
from pytest_django.asserts import assertContains, assertNotContains
from django.urls import reverse
from recipehub.factories import RecipeFactory, ReviewFactory


@pytest.mark.django_db
def test_recipe_detail_review_owner_cannot_rate(client, users_list):
    # Testing that recipe owners cannot rate their own recipes
    recipe_owner_user, first_simple_user, second_simple_user = users_list.values()
    approved_recipe = RecipeFactory.create(user=recipe_owner_user, slug="fish", approved=True)

    ReviewFactory.create(user=first_simple_user, recipe=approved_recipe, rating=5)
    ReviewFactory.create(user=second_simple_user, recipe=approved_recipe, rating=4)

    client.force_login(recipe_owner_user)
    response = client.get(reverse('recipes:recipe-detail', kwargs={'slug': approved_recipe.slug}))

    # Testing page response
    assert response.status_code == 200
    # Testing owner cannot see rating form
    assertNotContains(response, "Rate this recipe")
    # Testing average rating calculation
    assert response.context['average_rating'] == pytest.approx(4.5)


@pytest.mark.django_db
def test_recipe_detail_review_other_user_can_rate(client, users_list):
    # Testing that other users can rate recipes
    recipe_owner_user, first_simple_user, second_simple_user = users_list.values()
    recipe_from_another_user = RecipeFactory.create(user=first_simple_user, slug="pizza", approved=True)

    client.force_login(recipe_owner_user)
    response = client.get(reverse('recipes:recipe-detail', kwargs={'slug': recipe_from_another_user.slug}))

    # Testing page response
    assert response.status_code == 200
    # Testing rating form is visible
    assertContains(response, "Rate this recipe")
