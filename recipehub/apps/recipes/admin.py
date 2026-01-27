from django.contrib import admin
from recipehub.apps.recipes.models import Recipe, Category


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "category", "name", "moderation_status"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name"]
