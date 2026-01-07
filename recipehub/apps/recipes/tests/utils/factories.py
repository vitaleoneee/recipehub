from django.contrib.auth import get_user_model
from recipehub.apps.recipes.models import Recipe, Category
import factory


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    username = factory.Sequence(lambda n: f"user{n}")


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Sequence(lambda n: f"Category {n}")


class RecipeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Recipe

    user = factory.SubFactory(UserFactory)
    category = factory.SubFactory(CategoryFactory)
    name = factory.Sequence(lambda n: f"Recipe {n}")
    slug = factory.Sequence(lambda n: f"recipe-{n}")
    servings = 2
