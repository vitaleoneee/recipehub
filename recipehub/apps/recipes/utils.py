import os
import uuid

from django.utils.text import slugify
from typing import Any
from django.core.exceptions import ValidationError
from django.core.cache import cache

from django.apps import apps
from recipehub.redis import r


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
    Save recipe photo in the folder - media/recipes/<username>/<filename>
    """
    ext = os.path.splitext(filename)[1].lower()
    return f"recipes/{instance.user.username}/{uuid.uuid4()}{ext}"


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
            raise ValidationError("Each line must be in format: ingredient - quantity")

        if not name.replace(" ", "").isalpha():
            raise ValidationError(f"Invalid ingredient name: {name}")

        if not quantity:
            raise ValidationError(f"Quantity is missing for ingredient: {name}")

        if " - " in quantity:
            raise ValidationError(f"Invalid quantity format: '{line}'")

        normalized_lines.append(f"{name.lower()} - {quantity}")

    return "\n".join(normalized_lines)


def get_best_recipes() -> list[Any]:
    """
    Returns top 4 rated recipes from Redis.
    """

    Recipe = apps.get_model("recipes", "Recipe")

    best_recipes = cache.get("best_recipes")
    if not best_recipes:
        top_ids = r.zrevrange("recipe:ratings", 0, 3)

        if not top_ids:
            return []

        top_ids = [int(i) for i in top_ids]
        recipes = Recipe.objects.filter(id__in=top_ids)

        recipe_map = {recipe.id: recipe for recipe in recipes}
        best_recipes = [recipe_map[i] for i in top_ids if i in recipe_map]

        cache.set("best_recipes", best_recipes, 60 * 10)

    return best_recipes
