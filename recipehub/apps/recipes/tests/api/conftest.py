import pytest

from rest_framework.test import APIClient

from recipehub.factories import CategoryFactory


@pytest.fixture()
def api_client():
    return APIClient()


@pytest.fixture()
def authenticated_client(users_list):
    client = APIClient()
    user = users_list["first_simple_user"]
    client.force_authenticate(user=user)
    return client


@pytest.fixture()
def admin_client(api_client, users_list):
    user = users_list["first_simple_user"]
    user.is_staff = True
    user.save()
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture()
def category():
    return CategoryFactory()


@pytest.fixture()
def category_data():
    return {"name": "test"}
