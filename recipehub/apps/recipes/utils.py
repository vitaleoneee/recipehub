import os
import uuid


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
