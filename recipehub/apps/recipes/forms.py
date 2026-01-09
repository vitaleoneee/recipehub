from django import forms

from recipehub.apps.recipes.models import Recipe


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ["category", "name", "announcement_text", "photo", "ingredients", "recipe_text", "servings",
                  "cooking_time", "calories"]
