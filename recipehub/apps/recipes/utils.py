import os
import uuid

from django.utils.text import slugify


def valid_extension(filename):
    ext = filename.lower()
    if ext.endswith(".jpg") or ext.endswith(".jpeg"):
        return "JPEG"
    elif ext.endswith(".png"):
        return "PNG"
    else:
        raise ValueError("Unsupported image format")


def reformate_ingredients(raw_ingredients: str) -> list:
    return [i.strip() for i in raw_ingredients.strip().split(",")]


def generate_unique_slug(instance, slugify_value):
    base_slug = slugify(slugify_value)
    slug = base_slug
    counter = 1
    while instance.__class__.objects.filter(slug=slug).exclude(pk=instance.pk).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
    return slug


def user_photo_upload_to(instance, filename):
    """
    Save user photo in the folder - media/user-photo/<filename>
    """
    ext = os.path.splitext(filename)[1].lower()
    return f"user-photo/{instance.username}{ext}"


def recipe_photo_upload_to(instance, filename):
    """
    Save recipe photo in the folder - media/recipes/<filename>
    """
    ext = os.path.splitext(filename)[1].lower()
    return f"recipes/{instance.user.username}/{instance.slug}/{uuid.uuid4()}{ext}"
