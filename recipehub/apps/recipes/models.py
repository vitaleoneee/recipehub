from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.text import slugify

from recipehub.apps.recipes.utils import compress_images, recipe_photo_upload_to

User = get_user_model()


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="recipes")
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="recipes"
    )
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    announcement_text = models.TextField(blank=True)
    photo = models.ImageField(upload_to=recipe_photo_upload_to, blank=True, null=True)
    ingredients = models.TextField(
        help_text="Enter each ingredient on a new line and in the following order: ingredient name - quantity.",
        blank=True,
    )
    recipe_text = models.TextField(blank=True, help_text="The text of the recipe")
    servings = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )
    cooking_time = models.IntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1)],
        help_text="Cooking time in minutes",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)
    calories = models.IntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        help_text="Calories per serving",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f'"{self.name}" from {self.user.username}'

    def save(self, *args, **kwargs):
        # Compress images
        if self.photo and not hasattr(self.photo, "_compressed"):
            new_photo = compress_images(self.photo)
            new_photo._compressed = True
            self.photo = new_photo

        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def clean(self):
        if not self.ingredients:
            return

        normalized_lines = []
        lines = self.ingredients.splitlines()

        for line in lines:
            try:
                name, quantity = map(str.strip, line.split("-", 1))
            except ValueError:
                raise ValidationError(
                    {
                        "ingredients": (
                            "Each line must be in format: ingredient - quantity"
                        )
                    }
                )

            if not name.replace(" ", "").isalpha():
                raise ValidationError(
                    {"ingredients": f"Invalid ingredient name: {name}"}
                )

            if not quantity:
                raise ValidationError(
                    {"ingredients": f"Quantity is missing for ingredient: {name}"}
                )

            normalized_lines.append(f"{name.lower()} - {quantity}")

        self.ingredients = "\n".join(normalized_lines)
