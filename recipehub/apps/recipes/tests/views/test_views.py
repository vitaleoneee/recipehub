import pytest
from pytest_django.asserts import assertTemplateUsed, assertContains, assertNotContains
from django.urls import reverse

from recipehub.apps.recipes.tests.factories import RecipeFactory, ReviewFactory, UserRecipeFavoriteFactory


@pytest.mark.django_db
def test_index_view(client):
    """ Index page test. The template and context are checked for correctness. """

    response = client.get(reverse('recipes:index'))
    assert response.status_code == 200
    assertTemplateUsed(response, 'recipes/index.html')
    assert response.context['home_active'] == True


@pytest.mark.django_db
def test_recipe_list_view_with_pagination(client):
    """Recipe list page test with pagination.
       Checks template, context, approved recipes only,
       and proper pagination behavior.
    """

    approved_recipe1 = RecipeFactory.create(slug="fish-1", approved=True)
    approved_recipe2 = RecipeFactory.create(slug="fish-2", approved=True)
    approved_recipe3 = RecipeFactory.create(slug="fish-3", approved=True)
    approved_recipe4 = RecipeFactory.create(slug="fish-4", approved=True)
    unapproved_recipe = RecipeFactory.create(slug="pizza", approved=False)

    response = client.get(reverse('recipes:recipes-list'))
    assert response.status_code == 200
    assertTemplateUsed(response, 'recipes/recipe_list.html')

    recipes_page = response.context['recipes']
    assert response.context['list_active'] == True

    assert len(recipes_page) == 2
    assert approved_recipe1 in recipes_page
    assert approved_recipe2 in recipes_page
    assert approved_recipe3 not in recipes_page
    assert unapproved_recipe not in recipes_page

    assertContains(response, approved_recipe1.name)
    assertContains(response, approved_recipe2.name)
    assertNotContains(response, approved_recipe3.name)
    assertNotContains(response, unapproved_recipe.name)

    response_page2 = client.get(reverse('recipes:recipes-list') + '?page=2')
    recipes_page2 = response_page2.context['recipes']
    assert len(recipes_page2) == 2
    assert approved_recipe3 in recipes_page2
    assert approved_recipe4 in recipes_page2
    assert approved_recipe1 not in recipes_page2

    response_page3 = client.get(reverse('recipes:recipes-list') + '?page=3')
    assert response_page3.status_code == 404


@pytest.mark.django_db
def test_recipe_detail_status_code(client, users_list):
    """ Recipe detail code status test.
        Template validity is checked, redirect to log in if the user is not logged in
        and an error is returned if the recipe is not found.
    """
    recipe_owner_user = users_list["recipe_owner_user"]
    approved_recipe = RecipeFactory.create(user=recipe_owner_user, slug="fish", approved=True)
    unapproved_recipe = RecipeFactory.create(user=recipe_owner_user, slug="pizza", approved=False)

    redirection_response = client.get(reverse('recipes:recipe-detail', kwargs={'slug': approved_recipe.slug}))
    assert redirection_response.status_code == 302
    assert redirection_response.url.startswith('/accounts/login/')

    client.force_login(recipe_owner_user)

    bad_response = client.get(reverse('recipes:recipe-detail', kwargs={'slug': unapproved_recipe.slug}))
    assert bad_response.status_code == 404

    good_response = client.get(reverse('recipes:recipe-detail', kwargs={'slug': approved_recipe.slug}))
    assertTemplateUsed(good_response, 'recipes/recipe_detail.html')
    assert good_response.status_code == 200


@pytest.mark.django_db
def test_recipe_detail_review(client, users_list):
    """ Recipe detail reviews test.
        This checks whether owners are prohibited from rating recipes
        and whether the average rating value is correctly calculated.
    """
    recipe_owner_user, first_simple_user, second_simple_user = users_list.values()

    approved_recipe = RecipeFactory.create(user=recipe_owner_user, slug="fish", approved=True)
    recipe_from_another_user = RecipeFactory.create(user=first_simple_user, slug="pizza", approved=True)

    ReviewFactory.create(user=first_simple_user, recipe=approved_recipe, rating=5)
    ReviewFactory.create(user=second_simple_user, recipe=approved_recipe, rating=4)

    client.force_login(recipe_owner_user)
    response = client.get(reverse('recipes:recipe-detail', kwargs={'slug': approved_recipe.slug}))
    assert response.status_code == 200
    assertNotContains(response, "Rate this recipe")
    assert response.context['average_rating'] == pytest.approx(4.5)

    response = client.get(reverse('recipes:recipe-detail', kwargs={'slug': recipe_from_another_user.slug}))
    assert response.status_code == 200
    assertContains(response, "Rate this recipe")


@pytest.mark.django_db
def test_recipe_detail_favorite(client, users_list):
    """ A favorite recipe test.
        It checks whether the recipe can be added or removed from favorites
        and whether the recipe owners can choose not to do either.
    """
    recipe_owner_user, first_simple_user, second_simple_user = users_list.values()

    recipe_from_owner_user = RecipeFactory.create(user=recipe_owner_user, slug="fish", approved=True)
    recipe_from_another_user = RecipeFactory.create(user=first_simple_user, slug="pizza", approved=True)
    recipe_from_second_user = RecipeFactory.create(user=second_simple_user, slug="borsh", approved=True)

    UserRecipeFavoriteFactory.create(user=recipe_owner_user, recipe=recipe_from_another_user)

    client.force_login(recipe_owner_user)
    response = client.get(reverse('recipes:recipe-detail', kwargs={'slug': recipe_from_another_user.slug}))
    assert response.status_code == 200
    assertContains(response, "In Favorites")
    assert response.context['is_favorited'] == True

    response = client.get(reverse('recipes:recipe-detail', kwargs={'slug': recipe_from_second_user.slug}))
    assert response.status_code == 200
    assertContains(response, "Add to Favorites")

    response = client.get(reverse('recipes:recipe-detail', kwargs={'slug': recipe_from_owner_user.slug}))
    assert response.status_code == 200
    assertNotContains(response, "Add to Favorites")
    assertNotContains(response, "In Favorites")
