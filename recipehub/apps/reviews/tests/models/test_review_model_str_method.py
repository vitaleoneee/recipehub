import pytest
from recipehub.factories import UserFactory, ReviewFactory


@pytest.mark.parametrize(
    "username,rating,expected",
    [
        ("Vitalii", 5, "Vitalii - 5"),
        ("Ben", 4, "Ben - 4"),
        ("Alex", 3, "Alex - 3"),
    ],
)
@pytest.mark.django_db
def test_review_model_str_method(username, rating, expected):
    user = UserFactory.create(username=username)
    review = ReviewFactory.create(user=user, rating=rating)

    assert str(review) == expected

