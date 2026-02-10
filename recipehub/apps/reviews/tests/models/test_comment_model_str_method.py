import pytest
from recipehub.factories import CommentFactory, UserFactory
from freezegun import freeze_time


@pytest.mark.parametrize(
    "username",
    ["Vitalii", "Ben", "Alex"],
)
@pytest.mark.django_db
@freeze_time("2020-01-01 10:00:00")
class TestCommentModel:
    """Model tests for Comment"""

    def test_comment_model_str_method(self, username):
        user = UserFactory.create(username=username)
        comment1 = CommentFactory.create(
            user=user,
        )
        assert str(comment1) == f"{user.username} - 01-01-2020 10:00"
