import pytest

from recipehub.apps.recipes.utils import reformate_ingredients


@pytest.mark.parametrize(
    "raw_ingredients,expected",
    [
        ("    tomato,    cherry,banana", ["tomato", "cherry", "banana"]),
        ("\n\n\napple,rice,potato", ["apple", "rice", "potato"]),
        ("\nmilk,chocolate,ice-cream\n", ["milk", "chocolate", "ice-cream"]),
    ],
)
class TestReformatIngredients:
    """Tests for reformate_ingredients utility"""

    def test_reformat_ingredients_returns_list(self, raw_ingredients, expected):
        assert reformate_ingredients(raw_ingredients) == expected
        assert isinstance(reformate_ingredients(raw_ingredients), list)
