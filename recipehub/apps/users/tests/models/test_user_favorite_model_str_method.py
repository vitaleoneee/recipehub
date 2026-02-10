import pytest
from recipehub.factories import RecipeFactory, UserFactory, UserRecipeFavoriteFactory


@pytest.mark.parametrize(
    "name,username,expected",
    [
        ("Pizza Carbonara", "vitaleoneee", "vitaleoneee - Pizza Carbonara"),
        ("Fish", "IVAN", "IVAN - Fish"),
        ("Desert", "CHERRY451", "CHERRY451 - Desert"),
    ],
)
@pytest.mark.django_db
class TestUserRecipeFavoriteModel:
    """Tests for UserRecipeFavorite model string representation"""

    def test_user_favorite_model_str_method(self, name, username, expected):
        user = UserFactory.create(username=username)
        recipe = RecipeFactory.create(name=name, user=user)
        user_recipe_favorite = UserRecipeFavoriteFactory.create(
            user=user, recipe=recipe
        )

        assert str(user_recipe_favorite) == expected
