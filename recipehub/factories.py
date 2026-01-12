import random

import factory
from django.contrib.auth import get_user_model
from recipehub.apps.recipes.models import Recipe, Category
from recipehub.apps.reviews.models import Review, Comment
from recipehub.apps.users.models import UserRecipeFavorite


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


class ReviewFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Review

    recipe = factory.SubFactory(RecipeFactory)
    user = factory.SubFactory(UserFactory)
    rating = 4


class UserRecipeFavoriteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserRecipeFavorite

    recipe = factory.SubFactory(RecipeFactory)
    user = factory.SubFactory(UserFactory)


class CommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Comment

    recipe = factory.SubFactory(RecipeFactory)
    user = factory.SubFactory(UserFactory)
    body = factory.Sequence(lambda n: f"Comment {n}")
