import pytest
from pytest_django.asserts import assertContains
from django.urls import reverse
from recipehub.factories import RecipeFactory, CommentFactory


@pytest.mark.django_db
def test_recipe_detail_comment(client, users_list):
    # Testing comment display and pagination
    comment_owner_user, first_simple_user, second_simple_user, _ = users_list.values()
    recipe_from_comment_owner_user = RecipeFactory.create(
        user=comment_owner_user, slug="fish", moderation_status="approved"
    )

    # Creating comments
    first_comment = CommentFactory.create(
        user=first_simple_user, recipe=recipe_from_comment_owner_user
    )
    CommentFactory.create(
        user=comment_owner_user, recipe=recipe_from_comment_owner_user
    )
    for _ in range(4):
        CommentFactory.create(
            user=second_simple_user, recipe=recipe_from_comment_owner_user
        )

    client.force_login(comment_owner_user)

    # Testing first page comments
    response = client.get(
        reverse(
            "recipes:recipe-detail",
            kwargs={"slug": recipe_from_comment_owner_user.slug},
        )
    )
    assert response.status_code == 200
    assertContains(
        response, '<span class="badge bg-warning text-dark ms-1">Author</span>'
    )
    assert len(response.context["comments"].paginator.object_list) == 6

    # Testing second page pagination
    response_page2 = client.get(
        reverse(
            "recipes:recipe-detail",
            kwargs={"slug": recipe_from_comment_owner_user.slug},
        )
        + "?page=2"
    )
    comments_page2 = response_page2.context["comments"]
    assert len(comments_page2) == 1
    assert first_comment in comments_page2

    # Testing invalid page number
    response_page3 = client.get(
        reverse(
            "recipes:recipe-detail",
            kwargs={"slug": recipe_from_comment_owner_user.slug},
        )
        + "?page=1000"
    )
    assert response_page3.status_code == 200
    assert response_page3.wsgi_request.GET["page"] == "1000"
    assert len(response_page2.context["comments"]) == 1
