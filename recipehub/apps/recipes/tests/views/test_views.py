import pytest
from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.parametrize(
    "url,context_key",
    [("recipes:index", "home_active"), ("recipes:recipes-list", "list_active")],
)
def test_views(client, url, context_key):
    response = client.get(reverse(url))
    assert response.status_code == 200
    assert response.context is not None
    assert response.context[context_key] is True
