import pytest

from recipehub.factories import RecipeFactory, UserFactory
from recipehub.apps.recipes.utils import user_photo_upload_to, recipe_photo_upload_to


@pytest.mark.parametrize(
    "filename,expected_path",
    [
        ("avatar.JPG", "user-photo/test.jpg"),
        ("my-photo.png", "user-photo/test.png"),
        ("frer234gfqw3rf.jpeg", "user-photo/test.jpeg"),
    ],
)
def test_success_user_photo_upload_to(filename, expected_path):
    user = UserFactory.build(username="test")
    assert user_photo_upload_to(user, filename) == expected_path


@pytest.mark.parametrize(
    "filename,expected_path",
    [
        (
            "hello-world.JPG",
            "recipes/test/fish/a596b366-befa-42d1-870a-b4e7fddd9eba.jpg",
        ),
        ("1hellO1.png", "recipes/test/fish/a596b366-befa-42d1-870a-b4e7fddd9eba.png"),
        (
            "TEST1234.jpeg",
            "recipes/test/fish/a596b366-befa-42d1-870a-b4e7fddd9eba.jpeg",
        ),
    ],
)
def test_success_recipe_photo_upload_to(filename, expected_path, mocker):
    recipe = RecipeFactory.build(user__username="test", slug="fish")
    mocker.patch(
        "recipehub.apps.recipes.utils.uuid.uuid4",
        return_value="a596b366-befa-42d1-870a-b4e7fddd9eba",
    )

    assert recipe_photo_upload_to(recipe, filename) == expected_path
