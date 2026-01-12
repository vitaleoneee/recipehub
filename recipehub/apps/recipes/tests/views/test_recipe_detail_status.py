import pytest
from pytest_django.asserts import assertTemplateUsed
from django.urls import reverse
from recipehub.factories import RecipeFactory


@pytest.mark.django_db
def test_recipe_detail_status_code(client, users_list):
    # Testing recipe detail view status codes and template
    recipe_owner_user = users_list["recipe_owner_user"]
    approved_recipe = RecipeFactory.create(user=recipe_owner_user, slug="fish", approved=True)
    unapproved_recipe = RecipeFactory.create(user=recipe_owner_user, slug="pizza", approved=False)

    # Testing redirection to login for anonymous users
    redirection_response = client.get(reverse('recipes:recipe-detail', kwargs={'slug': approved_recipe.slug}))
    assert redirection_response.status_code == 302
    assert redirection_response.url.startswith('/accounts/login/')

    client.force_login(recipe_owner_user)

    # Testing 404 for unapproved recipe
    bad_response = client.get(reverse('recipes:recipe-detail', kwargs={'slug': unapproved_recipe.slug}))
    assert bad_response.status_code == 404

    # Testing approved recipe detail loads correctly
    good_response = client.get(reverse('recipes:recipe-detail', kwargs={'slug': approved_recipe.slug}))
    assert good_response.status_code == 200
    assertTemplateUsed(good_response, 'recipes/recipe_detail.html')
