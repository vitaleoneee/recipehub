import pytest
from recipehub.factories import RecipeFactory, UserFactory


@pytest.mark.parametrize(
    "name,username,expected",
    [
        ("Pizza Carbonara", "Vitalii", '"Pizza Carbonara" from Vitalii'),
        ("Fish", "Ben", '"Fish" from Ben'),
        ("Desert", "Alex", '"Desert" from Alex'),
    ],
)
@pytest.mark.django_db
def test_recipe_model_str_method(name, username, expected):
    user = UserFactory.create(username=username)
    recipe = RecipeFactory.create(name=name, user=user)

    assert str(recipe) == expected
