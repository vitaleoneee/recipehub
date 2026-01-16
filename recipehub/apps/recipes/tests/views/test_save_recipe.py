import json

import pytest
from django.urls import reverse

from recipehub.apps.users.models import UserRecipeFavorite
from recipehub.factories import RecipeFactory, UserRecipeFavoriteFactory


@pytest.mark.django_db
def test_save_recipe_missing_slug(client, users_list):
    user = users_list["first_simple_user"]
    client.force_login(user)

    # Send data to post request without slug
    response = client.post(
        reverse("recipes:save-recipe"),
        data=json.dumps({}),
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.json()["error"] == "Missing fields"


@pytest.mark.django_db
def test_save_recipe_not_found(client, users_list):
    user = users_list["first_simple_user"]
    client.force_login(user)

    # Sending data in a POST request - invalid recipe
    response = client.post(
        reverse("recipes:save-recipe"),
        data=json.dumps({"slug": "fish"}),
        content_type="application/json",
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_save_recipe_success(client, users_list):
    user = users_list["first_simple_user"]
    recipe = RecipeFactory.create(slug="fish")
    client.force_login(user)

    # Sending data in a POST request - adding to favorites
    response = client.post(
        reverse("recipes:save-recipe"),
        data=json.dumps({"slug": recipe.slug}),
        content_type="application/json",
    )
    data = response.json()
    assert data["status"] == "ok"
    assert data["is_favorited"]
    assert UserRecipeFavorite.objects.filter(user=user, recipe=recipe).exists()


@pytest.mark.django_db
def test_unsave_recipe_success(client, users_list):
    user = users_list["first_simple_user"]
    recipe = RecipeFactory.create(slug="fish")
    UserRecipeFavoriteFactory.create(user=user, recipe=recipe)
    client.force_login(user)

    # Sending data in a POST request - remove from favorites
    response = client.post(
        reverse("recipes:save-recipe"),
        data=json.dumps({"slug": recipe.slug}),
        content_type="application/json",
    )
    data = response.json()
    assert data["status"] == "ok"
    assert not response.json()["is_favorited"]
    assert not UserRecipeFavorite.objects.filter(user=user, recipe=recipe).exists()


@pytest.mark.django_db
def test_save_recipe_toggle(client, users_list):
    user = users_list["first_simple_user"]
    recipe = RecipeFactory.create(slug="fish")
    client.force_login(user)

    # Sending data in a POST request - adding to favorites
    response = client.post(
        reverse("recipes:save-recipe"),
        data=json.dumps({"slug": recipe.slug}),
        content_type="application/json",
    )
    assert response.json()["is_favorited"]

    # Sending data in a POST request - remove from favorites
    response = client.post(
        reverse("recipes:save-recipe"),
        data=json.dumps({"slug": recipe.slug}),
        content_type="application/json",
    )
    assert not response.json()["is_favorited"]

    assert not UserRecipeFavorite.objects.filter(user=user, recipe=recipe).exists()
