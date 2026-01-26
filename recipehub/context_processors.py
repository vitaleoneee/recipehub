from recipehub.redis import r
from recipehub.apps.recipes.models import Recipe


def redis_best_recipes(request):
    """
    Returns top 4 rated recipes from Redis.
    """
    top_ids = r.zrevrange("recipe:ratings", 0, 3)
    if not top_ids:
        return {"best_recipes": []}
    top_ids = [int(i) for i in top_ids]

    recipes = Recipe.objects.filter(id__in=top_ids)

    recipe_map = {recipe.id: recipe for recipe in recipes}
    best_recipes = [recipe_map[i] for i in top_ids if i in recipe_map]

    return {
        "best_recipes": best_recipes,
    }
