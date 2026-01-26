from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.urls import reverse

from recipehub.apps.recipes.utils import recipe_photo_upload_to, generate_unique_slug

User = get_user_model()

APPROVED_CHOICES = [
    ("approved", "Approved"),
    ("rejected", "Rejected"),
    ("in_process", "In Process"),
]


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, self.name)
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
        help_text="Enter each ingredient on a new line and in the following order: ingredient name - quantity",
    )
    recipe_text = models.TextField(blank=True, help_text="The text of the recipe")
    servings = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text="Number of servings",
    )
    cooking_time = models.IntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1)],
        help_text="Cooking time in minutes",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    moderation_status = models.CharField(
        max_length=20, choices=APPROVED_CHOICES, default="in_process"
    )
    calories = models.IntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        help_text="Calories per serving",
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f'"{self.name}" from {self.user.username}'

    def get_absolute_url(self):
        return reverse("recipes:recipe-detail", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, self.name)
        super().save(*args, **kwargs)
