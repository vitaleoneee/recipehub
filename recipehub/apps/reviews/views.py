from django.contrib.auth.decorators import login_required
from django.db.models.aggregates import Avg
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from recipehub.apps.recipes.decorators import require_post_json
from recipehub.apps.recipes.models import Recipe
from recipehub.apps.reviews.models import Review


@login_required
@require_post_json
def create_review(request):
    data = request.json_data

    slug = data.get("slug")
    rating = data.get("rating")

    if slug is None or rating is None:
        return JsonResponse({"error": "Missing fields"}, status=400)

    recipe = get_object_or_404(Recipe, slug=slug)

    review_obj, created = Review.objects.update_or_create(
        recipe=recipe, user=request.user, defaults={"rating": rating}
    )

    updated_average_rating = Review.objects.filter(recipe=recipe).aggregate(
        Avg("rating")
    )["rating__avg"]

    return JsonResponse(
        {
            "status": "ok",
            "rating": rating,
            "updated": not created,
            "average_rating": updated_average_rating,
        }
    )
