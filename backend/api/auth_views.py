import json

from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_GET, require_POST


def user_data(user):
    return {
        "id": user.pk,
        "username": user.get_username(),
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_staff": user.is_staff,
    }


@never_cache
@require_GET
def csrf_token(request):
    return JsonResponse({"csrfToken": get_token(request)})


@never_cache
@require_POST
@csrf_protect
def login_view(request):
    if request.content_type != "application/json":
        return JsonResponse(
            {"detail": "Send credentials as application/json."},
            status=415,
        )

    try:
        data = json.loads(request.body)
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({"detail": "Invalid JSON."}, status=400)

    if not isinstance(data, dict):
        return JsonResponse(
            {"detail": "Expected a JSON object."},
            status=400,
        )

    username = data.get("username")
    password = data.get("password")

    if (
        not isinstance(username, str)
        or not isinstance(password, str)
        or not username.strip()
        or not password
        or len(username) > 150
        or len(password) > 4096
    ):
        return JsonResponse(
            {"detail": "Provide a valid username and password."},
            status=400,
        )

    user = authenticate(
        request,
        username=username.strip(),
        password=password,
    )

    if user is None:
        return JsonResponse(
            {"detail": "Invalid username or password."},
            status=401,
        )

    if not user.is_active or not user.is_staff:
        return JsonResponse(
            {"detail": "An active staff account is required."},
            status=403,
        )

    login(request, user)
    return JsonResponse({
        "user": user_data(user),
        "csrfToken": get_token(request),
    })


@never_cache
@require_GET
def current_user(request):
    if not request.user.is_authenticated:
        return JsonResponse({"detail": "Please sign in."}, status=401)

    if not request.user.is_active or not request.user.is_staff:
        return JsonResponse(
            {"detail": "An active staff account is required."},
            status=403,
        )

    return JsonResponse({"user": user_data(request.user)})


@never_cache
@require_POST
@csrf_protect
def logout_view(request):
    logout(request)
    return JsonResponse({
        "detail": "Signed out.",
        "csrfToken": get_token(request),
    })
