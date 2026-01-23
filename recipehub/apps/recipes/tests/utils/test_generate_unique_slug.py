import pytest

from recipehub.apps.recipes.utils import generate_unique_slug
from recipehub.factories import RecipeFactory


@pytest.mark.parametrize(
    "name,expected", [("fish", "fish"), ("the best fish", "the-best-fish")]
)
@pytest.mark.django_db
def test_generate_unique_slug(name, expected):
    recipe = RecipeFactory.create(name=name)
    assert generate_unique_slug(instance=recipe, slugify_value=recipe.name) == expected


@pytest.mark.django_db
def test_generate_unique_slug_with_collision():
    recipe1 = RecipeFactory.create(name="fish", slug=None)
    assert generate_unique_slug(instance=recipe1, slugify_value=recipe1.name) == "fish"

    recipe2 = RecipeFactory.create(name="fish", slug=None)
    assert (
        generate_unique_slug(instance=recipe2, slugify_value=recipe2.name) == "fish-1"
    )

    recipe3 = RecipeFactory.create(name="fish", slug=None)
    assert (
        generate_unique_slug(instance=recipe3, slugify_value=recipe3.name) == "fish-2"
    )
