from django import forms

from recipehub.apps.recipes.models import Recipe
from recipehub.apps.recipes.utils import validate_ingredients_format


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
        value = self.cleaned_data.get("ingredients", "")
        return validate_ingredients_format(value)
