from typing import Any

from django.http import HttpRequest

from recipehub.apps.recipes.utils import get_best_recipes


def redis_best_recipes(request: HttpRequest) -> dict[str, Any]:
    """
    Returns top 4 rated recipes from Redis.
    Doesn't work for API
    """
    if (
        request.path.startswith("/api/")
        and request.path != "/api/recipes/best-recipes/"
    ):
        return {}

    best_recipes = get_best_recipes()

    return {
        "best_recipes": best_recipes,
    }
