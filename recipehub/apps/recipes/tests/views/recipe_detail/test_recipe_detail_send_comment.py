import pytest
from django.urls import reverse

from recipehub.apps.reviews.models import Comment
from recipehub.factories import RecipeFactory


@pytest.mark.django_db
def test_send_comment_without_data(client, users_list):
    user = users_list["first_simple_user"]
    recipe = RecipeFactory.create(moderation_status="approved")
    client.force_login(user)

    # Sending request without data
    response = client.post(
        reverse("recipes:recipe-detail", kwargs={"slug": recipe.slug}), data={}
    )
    assert response.status_code == 200
    assert Comment.objects.filter(user=user, recipe=recipe).count() == 0


@pytest.mark.django_db
def test_send_comment_with_data(client, users_list):
    user = users_list["first_simple_user"]
    recipe = RecipeFactory.create(moderation_status="approved")
    client.force_login(user)

    # Sending first comment
    response = client.post(
        reverse("recipes:recipe-detail", kwargs={"slug": recipe.slug}),
        data={"body": "Good recipe!"},
    )
    assert response.status_code == 302
    comment = Comment.objects.get(user=user)
    assert comment.body == "Good recipe!"
    assert comment.recipe == recipe

    # Sending second comment
    response = client.post(
        reverse("recipes:recipe-detail", kwargs={"slug": recipe.slug}),
        data={"body": "Very good recipe!"},
    )
    assert response.status_code == 302
    assert Comment.objects.filter(user=user, recipe=recipe).count() == 2
