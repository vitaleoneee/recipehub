from pathlib import Path

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

from recipehub.apps.recipes.forms import RecipeForm
from recipehub.apps.recipes.models import Recipe
from recipehub.factories import CategoryFactory


@pytest.mark.parametrize(
    "name,announcement_text,ingredients,recipe_text,servings,cooking_time,calories",
    [
        ("test1", "Good recipe", "tomato - 1", "Mix it", 2, 50, 50),
        ("TEST1", "GOOD RECIPE", "banana-41412ks", "bowl", 55, 134, 1111),
        ("tq1.51!", "its tasty", "potato- 1st", "nice!", 1, 1, 1),
    ],
)
@pytest.mark.django_db
def test_recipe_form_valid_various_inputs_without_photo(
    name, announcement_text, ingredients, recipe_text, servings, cooking_time, calories
):
    category = CategoryFactory.create()

    # Testing valid form
    form_data = {
        "category": category.id,
        "name": name,
        "announcement_text": announcement_text,
        "ingredients": ingredients,
        "recipe_text": recipe_text,
        "servings": servings,
        "cooking_time": cooking_time,
        "calories": calories,
    }
    form = RecipeForm(data=form_data)
    assert form.is_valid()


@pytest.mark.django_db
def test_add_recipe_with_photo(client, users_list):
    user = users_list["first_simple_user"]
    client.force_login(users_list["first_simple_user"])
    category = CategoryFactory.create()

    # Create photo
    image_path = Path(__file__).parent / "fixture_image" / "test_image.jpg"
    with open(image_path, "rb") as f:
        photo_content = f.read()
    photo = SimpleUploadedFile(
        "test-photo.jpg", photo_content, content_type="image/jpg"
    )

    # Create form-data
    form_data = {
        "category": category.id,
        "name": "test",
        "announcement_text": "test",
        "ingredients": "tomato - 1",
        "photo": photo,
        "recipe_text": "Tasty",
        "servings": 1,
        "cooking_time": 1,
        "calories": 1,
    }

    # Send post request
    response = client.post(reverse("recipes:recipe-add"), data=form_data)

    assert response.status_code == 302
    from recipehub.apps.recipes.models import Recipe

    recipe = Recipe.objects.get(name="test")
    assert recipe.user == user
    assert recipe.photo


@pytest.mark.django_db
def test_add_recipe_with_non_image_as_photo(client, users_list):
    user = users_list["first_simple_user"]
    client.force_login(user)
    category = CategoryFactory.create()

    # Create fake image
    fake_image = SimpleUploadedFile(
        name="fake.jpg",
        content=b"just plain text pretending to be jpeg",
        content_type="image/jpeg",
    )

    data = {
        "category": category.id,
        "name": "Fake image",
        "servings": 1,
        "ingredients": "tomato - 1",
        "photo": fake_image,
    }

    response = client.post(reverse("recipes:recipe-add"), data=data)

    assert response.status_code == 200
    assert "photo" in response.context["form"].errors
    assert not Recipe.objects.filter(name="Fake image").exists()


@pytest.mark.parametrize(
    "category_id,name,servings",
    [
        (32, "test", 1),
        (1, "2" * 105, 1),
        (1, "test1", -1),
    ],
)
@pytest.mark.django_db
def test_recipe_form_without_required_fields(category_id, name, servings):
    if category_id == 1:
        CategoryFactory.create(id=1)

    form_data = {
        "category": category_id,
        "name": name,
        "servings": servings,
    }
    form = RecipeForm(data=form_data)
    assert not form.is_valid()


@pytest.mark.django_db
def test_add_recipe_template(client, users_list):
    client.force_login(users_list["first_simple_user"])
    # Testing "add recipe" page loads correctly
    response = client.get(reverse("recipes:recipe-add"))
    assert response.status_code == 200
    # Testing correct template is used
    assertTemplateUsed(response, "recipes/recipe_add.html")
    # Testing context variable
    assert response.context["add_recipe_active"] is True
    assert isinstance(response.context["form"], RecipeForm)


@pytest.mark.parametrize(
    "ingredients,should_be_valid,expected_error",
    [
        ("Flour - 200g\nSugar - 80g", True, None),
        ("Flour - 200g - excess", False, "Invalid quantity format"),
        ("Flour200g", False, "Each line must be in format"),
        ("123-200g", False, "Invalid ingredient name"),
        ("123-", False, "Invalid quantity format"),
        ("  Sugar - 200g", True, None),
        ("", True, None),
        ("\n \n", True, None),
    ],
)
@pytest.mark.django_db
def test_add_recipe_clean_ingredients(ingredients, should_be_valid, expected_error):
    form = RecipeForm(data={"ingredients": ingredients})
    form.is_valid()  # launch all "clean_" functions
    if should_be_valid:
        assert "ingredients" not in form.errors
    else:
        assert "ingredients" in form.errors
