import pytest
import json
from django.urls import reverse
from recipehub.factories import RecipeFactory


@pytest.mark.django_db
def test_review_get_not_allowed(client, users_list):
    # Testing GET request returns 405
    _, first_user, _ = users_list.values()
    client.force_login(first_user)
    response = client.get(reverse("reviews:create-review"))
    assert response.status_code == 405


@pytest.mark.django_db
def test_review_post_missing_fields(client, users_list):
    # Testing POST without required fields returns 400
    _, first_user, _ = users_list.values()
    client.force_login(first_user)

    # Missing slug
    response = client.post(
        reverse("reviews:create-review"),
        data={"rating": 3},
        content_type="application/json",
    )
    assert response.status_code == 400

    # Missing rating
    response = client.post(
        reverse("reviews:create-review"),
        data={"slug": "fish"},
        content_type="application/json",
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_review_post_create(client, users_list):
    # Testing creation of a new review
    recipe_owner_user, first_user, _ = users_list.values()
    client.force_login(first_user)

    recipe = RecipeFactory.create(
        user=recipe_owner_user, slug="fish", moderation_status="approved"
    )

    # Sending valid POST request
    response = client.post(
        reverse("reviews:create-review"),
        data=json.dumps({"rating": 3, "slug": recipe.slug}),
        content_type="application/json",
    )
    data = response.json()

    assert response.status_code == 200
    assert data["status"] == "ok"
    assert data["rating"] == 3
    assert data["updated"] is False
    assert data["average_rating"] == 3


@pytest.mark.django_db
def test_review_post_update(client, users_list):
    # Testing update of an existing review
    recipe_owner_user, first_user, _ = users_list.values()
    client.force_login(first_user)

    recipe = RecipeFactory.create(
        user=recipe_owner_user, slug="fish", moderation_status="approved"
    )

    # Creating initial review
    client.post(
        reverse("reviews:create-review"),
        data=json.dumps({"rating": 3, "slug": recipe.slug}),
        content_type="application/json",
    )

    # Updating review
    response = client.post(
        reverse("reviews:create-review"),
        data=json.dumps({"rating": 5, "slug": recipe.slug}),
        content_type="application/json",
    )
    data = response.json()

    assert response.status_code == 200
    assert data["status"] == "ok"
    assert data["rating"] == 5
    assert data["updated"] is True
    assert data["average_rating"] == 5


@pytest.mark.django_db
def test_review_average_rating(client, users_list):
    # Testing average rating calculation with multiple reviews
    recipe_owner_user, first_user, second_user = users_list.values()

    client.force_login(first_user)
    recipe = RecipeFactory.create(
        user=recipe_owner_user, slug="fish", moderation_status="approved"
    )

    # First user adds a review
    client.post(
        reverse("reviews:create-review"),
        data=json.dumps({"rating": 5, "slug": recipe.slug}),
        content_type="application/json",
    )

    # Second user adds a review
    client.force_login(second_user)
    response = client.post(
        reverse("reviews:create-review"),
        data=json.dumps({"rating": 2, "slug": recipe.slug}),
        content_type="application/json",
    )
    data = response.json()

    assert response.status_code == 200
    assert data["status"] == "ok"
    assert data["rating"] == 2
    assert data["updated"] is False
    # Testing average rating
    assert data["average_rating"] == pytest.approx(3.5)
