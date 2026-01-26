import os
import uuid

from django.utils.text import slugify
from typing import Any
from django.core.exceptions import ValidationError


def valid_extension(filename: str) -> str:
    ext = filename.lower()
    if ext.endswith(".jpg") or ext.endswith(".jpeg"):
        return "JPEG"
    elif ext.endswith(".png"):
        return "PNG"
    else:
        raise ValueError("Unsupported image format")


def reformate_ingredients(raw_ingredients: str) -> list[str]:
    return [i.strip() for i in raw_ingredients.strip().split(",")]


def generate_unique_slug(instance: Any, slugify_value: str) -> str:
    """
    Generates a unique slug without collisions
    """
    base_slug = slugify(slugify_value)
    slug = base_slug
    counter = 1
    while instance.__class__.objects.filter(slug=slug).exclude(pk=instance.pk).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
    return slug


def user_photo_upload_to(instance: Any, filename: str) -> str:
    """
    Save user photo in the folder - media/user-photo/<filename>
    """
    ext = os.path.splitext(filename)[1].lower()
    return f"user-photo/{instance.username}{ext}"


def recipe_photo_upload_to(instance: Any, filename: str) -> str:
    """
    Save recipe photo in the folder - media/recipes/<filename>
    """
    ext = os.path.splitext(filename)[1].lower()
    return f"recipes/{instance.user.username}/{instance.slug}/{uuid.uuid4()}{ext}"


def validate_ingredients_format(value: str) -> str:
    value = value.strip()
    if not value:
        return value

    normalized_lines = []
    lines = value.splitlines()

    for line in lines:
        try:
            name, quantity = map(str.strip, line.split("-", 1))
        except ValueError:
            raise ValidationError(
                "Each line must be in format: ingredient - quantity"
            )

        if not name.replace(" ", "").isalpha():
            raise ValidationError(f"Invalid ingredient name: {name}")

        if not quantity:
            raise ValidationError(f"Quantity is missing for ingredient: {name}")

        if " - " in quantity:
            raise ValidationError(f"Invalid quantity format: '{line}'")

        normalized_lines.append(f"{name.lower()} - {quantity}")

    return "\n".join(normalized_lines)
