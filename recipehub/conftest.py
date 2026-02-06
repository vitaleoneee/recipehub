from io import BytesIO

import fakeredis
import pytest
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile

from recipehub.factories import UserFactory
import recipehub.redis as redis_module


@pytest.fixture
def valid_signup_data():
    """
    Basic valid data for registration
    """
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password1": "SecurePass123!",
        "password2": "SecurePass123!",
    }


@pytest.fixture
def sample_image():
    """
    Creates a test image
    """
    image = Image.new("RGB", (100, 100), color="red")
    image_io = BytesIO()
    image.save(image_io, format="JPEG")
    image_io.seek(0)
    return SimpleUploadedFile(
        "test_photo.jpg", image_io.read(), content_type="image/jpeg"
    )


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
        "admin_user": UserFactory.create(),
    }
