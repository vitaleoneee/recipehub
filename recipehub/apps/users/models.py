from django.contrib.auth.models import AbstractUser
from django.db import models

from recipehub.apps.recipes.utils import compress_images, user_photo_upload_to


class UserRecipeFavorite(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    recipe = models.ForeignKey("recipes.Recipe", on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)


class User(AbstractUser):
    date_of_birth = models.DateField(null=True, blank=True)
    photo = models.ImageField(upload_to=user_photo_upload_to, null=True, blank=True)
    favorites = models.ManyToManyField(
        "recipes.Recipe",
        through="UserRecipeFavorite",
        blank=True,
        related_name="favourites",
    )

    def save(self, *args, **kwargs):
        # Delete old photo if new photo was added
        if self.pk:
            old = type(self).objects.filter(pk=self.pk).first()
            if old and old.photo and old.photo.name != self.photo.name:
                old.photo.delete(save=False)

        # Compress images
        if self.photo and not hasattr(self.photo, "_compressed"):
            new_photo = compress_images(self.photo)
            new_photo._compressed = True
            self.photo = new_photo
        super().save(*args, **kwargs)
