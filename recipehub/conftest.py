import fakeredis
import pytest

from recipehub.factories import UserFactory
import recipehub.redis as redis_module


@pytest.fixture()
def fake_redis(monkeypatch):
    """
    Fixture for creating a fake redis
    """
    fake_client = fakeredis.FakeStrictRedis()
    monkeypatch.setattr(redis_module, "r", fake_client)
    return fake_client


@pytest.fixture()
def users_list():
    return {
        "recipe_owner_user": UserFactory.create(),
        "first_simple_user": UserFactory.create(),
        "second_simple_user": UserFactory.create(),
    }
