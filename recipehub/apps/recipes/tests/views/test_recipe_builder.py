import pytest
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed, assertContains, assertNotContains

from recipehub.factories import RecipeFactory


@pytest.mark.django_db
def test_recipe_builder_template(client, users_list):
    # The user is not logged in - redirect
    redirect_response = client.get(reverse("recipes:recipe-builder"))
    assert redirect_response.status_code == 302

    # The user is logged in - right template
    client.force_login(users_list["first_simple_user"])
    simple_response = client.get(reverse("recipes:recipe-builder"))
    assert simple_response.status_code == 200
    assertTemplateUsed(simple_response, "recipes/recipe_builder.html")


@pytest.mark.django_db
def test_recipe_builder_add_ingredients(client, users_list):
    client.force_login(users_list["first_simple_user"])
    response = client.post(
        reverse("recipes:recipe-builder"), data={"ingredients": "coffee, milk"}
    )
    assert response.status_code == 200
    assertContains(response, "coffee")
    assertContains(response, "milk")
    assert response.context["ingredients"] == ["coffee", "milk"]

    session = client.session
    assert session.get("ingredients") == ["coffee", "milk"]


@pytest.mark.django_db
def test_recipe_builder_add_ingredients_with_no_data(client, users_list):
    client.force_login(users_list["first_simple_user"])
    response = client.post(reverse("recipes:recipe-builder"), data={"ingredients": ""})
    assert response.status_code == 200
    assertContains(response, "No ingredients added yet...")
    assert response.context["ingredients"] == []

    session = client.session
    assert session.get("ingredients") is None


@pytest.mark.django_db
def test_recipe_builder_clear_ingredients(client, users_list):
    client.force_login(users_list["first_simple_user"])
    client.post(reverse("recipes:recipe-builder"), data={"ingredients": "tea, cheeps"})

    session = client.session
    assert session.get("ingredients") == ["tea", "cheeps"]

    clear_response = client.post(
        reverse("recipes:recipe-builder"), data={"clear_ingredients": "1"}
    )
    assert clear_response.status_code == 200
    assertNotContains(clear_response, "tea")
    assertNotContains(clear_response, "cheeps")
    assert clear_response.context["ingredients"] == []

    session = client.session
    assert session.get("ingredients") is None


@pytest.mark.django_db
def test_recipe_builder_find_recipes(client, users_list):
    client.force_login(users_list["first_simple_user"])
    recipe1 = RecipeFactory.create(
        name="Pizza Pepperoni", ingredients="tomato - 1ks", moderation_status="approved"
    )
    recipe2 = RecipeFactory.create(
        name="Taste Potato", ingredients="potato - 2ks", moderation_status="approved"
    )

    response = client.get(reverse("recipes:recipes-list") + "?ingredients=tomato")
    assert response.status_code == 200
    assertContains(response, f'<h5 class="card-title">{recipe1.name}</h5>')
    assertNotContains(response, f'<h5 class="card-title">{recipe2.name}</h5>')
