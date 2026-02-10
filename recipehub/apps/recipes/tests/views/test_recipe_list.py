import pytest
from django.urls import reverse
from recipehub.factories import RecipeFactory


@pytest.mark.django_db
class TestRecipeListView:
    """Tests for the recipe list and pagination"""

    def test_recipe_list_view_with_pagination(self, client, users_list):
        """Pagination returns only approved recipes and handles pages"""
        # Creating approved recipes with explicit users
        RecipeFactory.create(
            user=users_list["recipe_owner_user"],
            slug="fish-1",
            moderation_status="approved",
        )
        RecipeFactory.create(
            user=users_list["first_simple_user"],
            slug="fish-2",
            moderation_status="approved",
        )
        RecipeFactory.create(
            user=users_list["second_simple_user"],
            slug="fish-3",
            moderation_status="approved",
        )
        RecipeFactory.create(
            user=users_list["recipe_owner_user"],
            slug="fish-4",
            moderation_status="approved",
        )
        RecipeFactory.create(
            user=users_list["first_simple_user"],
            slug="pizza",
            moderation_status="rejected",
        )

        # First page
        response = client.get(reverse("recipes:recipes-list"))
        recipes_page = response.context["recipes"]
        slugs_page1 = [r.slug for r in recipes_page]

        # Testing pagination size
        assert len(recipes_page) == 2
        # Testing that only approved recipes are present
        assert all(slug.startswith("fish") for slug in slugs_page1)
        assert "pizza" not in slugs_page1

        # Second page
        response_page2 = client.get(reverse("recipes:recipes-list") + "?page=2")
        recipes_page2 = response_page2.context["recipes"]
        slugs_page2 = [r.slug for r in recipes_page2]

        # Testing pagination size
        assert len(recipes_page2) == 2
        # Testing that only approved recipes are present
        assert all(slug.startswith("fish") for slug in slugs_page2)
        assert "pizza" not in slugs_page2

        # Invalid page
        response_page3 = client.get(reverse("recipes:recipes-list") + "?page=1000")
        assert response_page3.status_code == 200
        assert response_page3.wsgi_request.GET["page"] == "1000"
