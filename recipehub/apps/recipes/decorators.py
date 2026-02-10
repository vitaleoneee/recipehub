import json
from functools import wraps
from django.http import JsonResponse


def require_post_json(view_func):
    """
    Ensures that the request is a POST request with a valid JSON payload.
    Parsed JSON is available as request.json_data.
    """

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.method != "POST":
            return JsonResponse({"error": "POST required"}, status=405)

        try:
            request.json_data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        return view_func(request, *args, **kwargs)

    return wrapper
