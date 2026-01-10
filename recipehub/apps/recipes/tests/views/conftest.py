import pytest

from recipehub.apps.recipes.tests.factories import UserFactory


@pytest.fixture()
def users_list():
    return {
        "recipe_owner_user": UserFactory.create(),
        "first_simple_user": UserFactory.create(),
        "second_simple_user": UserFactory.create(),
    }
