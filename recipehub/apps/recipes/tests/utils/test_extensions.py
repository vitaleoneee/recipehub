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
def test_valid_extensions(filename, res):
    assert valid_extension(filename) == res


@pytest.mark.parametrize("filename", ["cat.gif", "text", "mafin.txt"])
def test_invalid_extensions(filename):
    with pytest.raises(ValueError):
        valid_extension(filename)
