from django import forms
from django.core.exceptions import ValidationError

from recipehub.apps.recipes.models import Recipe


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = [
            "category",
            "name",
            "announcement_text",
            "photo",
            "ingredients",
            "recipe_text",
            "servings",
            "cooking_time",
            "calories",
        ]

    def clean_ingredients(self):
        ingredients = self.cleaned_data.get("ingredients", "").strip()

        if not ingredients:
            return ingredients

        normalized_lines = []
        lines = ingredients.splitlines()

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
