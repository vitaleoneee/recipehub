import pytest
from recipehub.apps.recipes.utils import valid_extension


@pytest.mark.parametrize(
    "filename,res",
    [
        ("test.JPG", "JPEG"),
        ("test.jpeg", "JPEG"),
        ("paint.png", "PNG"),
    ],
)
class TestValidExtensions:
    def test_valid_extensions(self, filename, res):
        assert valid_extension(filename) == res


@pytest.mark.parametrize("filename", ["cat.gif", "text", "mafin.txt"])
class TestInvalidExtensions:
    def test_invalid_extensions(self, filename):
        with pytest.raises(ValueError):
            valid_extension(filename)
