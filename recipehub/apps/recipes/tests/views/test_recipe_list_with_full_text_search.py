import pytest
from django.urls import reverse
from recipehub.factories import RecipeFactory


@pytest.mark.django_db
def test_recipe_list_view_with_pagination(client, users_list):
    # Creating approved recipes with explicit users
    first_fish_recipe = RecipeFactory.create(
        user=users_list["recipe_owner_user"],
        name="Fish",
        slug="fish",
        moderation_status=True,
    )
    second_fish_recipe = RecipeFactory.create(
        user=users_list["first_simple_user"],
        name="Fish",
        slug="fresh-fish",
        ingredients="tomato - 1ks",
        moderation_status="approved",
    )
    vareniki_recipe = RecipeFactory.create(
        user=users_list["second_simple_user"],
        recipe_text="Bake the dough",
        slug="vareniki",
        moderation_status="approved",
    )

    # "Fish" query page
    response = client.get(reverse("recipes:recipes-list") + "?search=Fish")
    search_recipes_page = response.context["recipes"]
    assert response.status_code == 200
    assert len(search_recipes_page) == 2
    assert first_fish_recipe in search_recipes_page
    assert second_fish_recipe in search_recipes_page

    # Unrecognized query page
    response = client.get(reverse("recipes:recipes-list") + "?search=dough")
    search_recipes_page = response.context["recipes"]
    assert response.status_code == 200
    assert len(search_recipes_page) == 1
    assert vareniki_recipe in search_recipes_page
