import os
import uuid

from io import BytesIO
from PIL import Image
from django.core.files import File


def compress_images(image):
    im = Image.open(image)
    width, height = im.size

    factor = 0.5
    new_width = int(width * factor)
    new_height = int(height * factor)
    im.thumbnail((new_width, new_height), Image.LANCZOS)

    # Determine format
    format_ = valid_extension(image.name)

    # Save to BytesIO
    im_io = BytesIO()
    if format_ == "JPEG":
        im = im.convert("RGB")
        im.save(im_io, format_, optimize=True, quality=70)
    else:  # PNG
        im.save(im_io, format_, optimize=True)

    im_io.seek(0)
    new_image = File(im_io, name=image.name)
    return new_image


def valid_extension(filename):
    ext = filename.lower()
    if ext.endswith(".jpg") or ext.endswith(".jpeg"):
        return "JPEG"
    elif ext.endswith(".png"):
        return "PNG"
    else:
        raise ValueError("Unsupported image format")


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
