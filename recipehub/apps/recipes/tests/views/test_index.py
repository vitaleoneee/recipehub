import pytest
from pytest_django.asserts import assertTemplateUsed
from django.urls import reverse


@pytest.mark.django_db
def test_index_view(client):
    # Testing index page loads correctly
    response = client.get(reverse('recipes:index'))
    assert response.status_code == 200
    # Testing correct template is used
    assertTemplateUsed(response, 'recipes/index.html')
    # Testing active context variable
    assert response.context['home_active'] is True
