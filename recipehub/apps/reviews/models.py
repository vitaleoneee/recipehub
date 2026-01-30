from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Review(models.Model):
    recipe = models.ForeignKey(
        "recipes.Recipe", on_delete=models.CASCADE, related_name="reviews"
    )
    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="reviews"
    )
    rating = models.FloatField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("recipe", "user")
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.user.username} - {int(self.rating)}"


class Comment(models.Model):
    recipe = models.ForeignKey(
        "recipes.Recipe", on_delete=models.CASCADE, related_name="comments"
    )
    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="comments"
    )
    body = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.created_at.strftime('%d-%m-%Y %H:%M')}"

    class Meta:
        ordering = ["-created_at"]
