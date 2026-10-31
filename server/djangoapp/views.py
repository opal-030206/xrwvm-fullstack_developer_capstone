"""JSON API views for the Cars Dealership application.

Every endpoint under ``/djangoapp/`` is consumed by the React frontend and is
also exercised directly with cURL in the capstone submission.
"""

import datetime
import json
import re

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import Dealer, Review
from .services import (
    car_makes_to_list,
    dealer_to_dict,
    review_to_dict,
    sentiment_for,
)


def _body(request):
    """Parse a JSON (or form-encoded) request body into a dict."""
    if not request.body:
        return request.POST.dict()
    try:
        parsed = json.loads(request.body.decode("utf-8"))
        return parsed if isinstance(parsed, dict) else {}
    except (ValueError, UnicodeDecodeError):
        return request.POST.dict()


def _user_payload(user):
    return {
        "userName": user.username,
        "firstName": user.first_name,
        "lastName": user.last_name,
        "email": user.email,
        "isStaff": user.is_staff,
        "status": "Authenticated",
    }


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------
@csrf_exempt
@require_http_methods(["POST"])
def login_user(request):
    """POST /djangoapp/login -> establish a session for *userName*."""
    data = _body(request)
    username = data.get("userName") or data.get("username") or ""
    password = data.get("password") or ""

    user = authenticate(request, username=username, password=password)
    if user is None:
        return JsonResponse(
            {
                "userName": username,
                "status": "Authentication failed",
                "message": "Invalid username or password.",
            },
            status=401,
        )

    login(request, user)
    return JsonResponse(_user_payload(user))


@csrf_exempt
@require_http_methods(["GET", "POST"])
def logout_user(request):
    """GET|POST /djangoapp/logout -> end the current session."""
    username = request.user.username if request.user.is_authenticated else None
    logout(request)
    return JsonResponse(
        {
            "userName": username,
            "status": "Logged out" if username else "No active session",
        }
    )


@csrf_exempt
@require_http_methods(["POST"])
def register_user(request):
    """POST /djangoapp/register -> create an account and log it in."""
    data = _body(request)
    username = (data.get("userName") or data.get("username") or "").strip()
    password = data.get("password") or ""
    first_name = (data.get("firstName") or "").strip()
    last_name = (data.get("lastName") or "").strip()
    email = (data.get("email") or "").strip()

    missing = [
        label
        for label, value in (
            ("Username", username),
            ("Password", password),
            ("First Name", first_name),
            ("Last Name", last_name),
            ("Email", email),
        )
        if not value
    ]
    if missing:
        return JsonResponse(
            {"status": "Registration failed",
             "message": f"Missing required field(s): {', '.join(missing)}."},
            status=400,
        )

    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[A-Za-z]{2,}", email):
        return JsonResponse(
            {"status": "Registration failed", "message": "Enter a valid email."},
            status=400,
        )

    if User.objects.filter(username=username).exists():
        return JsonResponse(
            {"status": "Registration failed",
             "message": f"The username '{username}' is already taken."},
            status=409,
        )

    user = User.objects.create_user(
        username=username,
        password=password,
        first_name=first_name,
        last_name=last_name,
        email=email,
    )
    login(request, user)
    return JsonResponse(_user_payload(user), status=201)


@require_http_methods(["GET"])
def session_info(request):
    """GET /djangoapp/session -> who am I? (never 401, so the UI can ask)"""
    if request.user.is_authenticated:
        payload = _user_payload(request.user)
        payload["loggedIn"] = True
        return JsonResponse(payload)
    return JsonResponse({"loggedIn": False, "userName": None})


# ---------------------------------------------------------------------------
# Dealers
# ---------------------------------------------------------------------------
@require_http_methods(["GET"])
def get_dealers(request):
    """GET /djangoapp/get_dealers -> every branch."""
    return JsonResponse([dealer_to_dict(d) for d in Dealer.objects.all()],
                        safe=False)


@require_http_methods(["GET"])
def get_dealer_by_id(request, dealer_id):
    """GET /djangoapp/get_dealer/<id> -> one branch."""
    try:
        dealer = Dealer.objects.get(pk=dealer_id)
    except Dealer.DoesNotExist:
        return JsonResponse(
            {"error": f"Dealer {dealer_id} not found."}, status=404
        )
    return JsonResponse(dealer_to_dict(dealer))


@require_http_methods(["GET"])
def get_dealers_by_state(request, state):
    """GET /djangoapp/get_dealers/<state> -> branches filtered by state."""
    dealers = Dealer.objects.filter(state__iexact=state)
    return JsonResponse([dealer_to_dict(d) for d in dealers], safe=False)


# ---------------------------------------------------------------------------
# Reviews
# ---------------------------------------------------------------------------
@require_http_methods(["GET"])
def get_dealer_reviews(request, dealer_id):
    """GET /djangoapp/reviews/dealer/<id> -> reviews for one branch."""
    if not Dealer.objects.filter(pk=dealer_id).exists():
        return JsonResponse(
            {"error": f"Dealer {dealer_id} not found."}, status=404
        )
    reviews = Review.objects.filter(dealer_id=dealer_id).select_related(
        "user", "dealer"
    )
    return JsonResponse([review_to_dict(r) for r in reviews], safe=False)


@csrf_exempt
@require_http_methods(["POST"])
def add_review(request):
    """POST /djangoapp/add_review -> store a review with its sentiment."""
    data = _body(request)

    if not request.user.is_authenticated:
        return JsonResponse(
            {"status": "Failed", "message": "You must be signed in to review."},
            status=401,
        )

    dealer_id = data.get("dealer_id") or data.get("dealerId")
    text = (data.get("review") or "").strip()

    if not dealer_id:
        return JsonResponse(
            {"status": "Failed", "message": "dealer_id is required."}, status=400
        )
    if not text:
        return JsonResponse(
            {"status": "Failed", "message": "Review text is required."}, status=400
        )
    if not Dealer.objects.filter(pk=dealer_id).exists():
        return JsonResponse(
            {"status": "Failed", "message": f"Dealer {dealer_id} not found."},
            status=404,
        )

    purchase_date = data.get("purchase_date") or data.get("purchaseDate") or None
    if purchase_date:
        try:
            purchase_date = datetime.date.fromisoformat(purchase_date)
        except ValueError:
            return JsonResponse(
                {"status": "Failed",
                 "message": "purchase_date must be YYYY-MM-DD."},
                status=400,
            )

    car_year = data.get("car_year") or data.get("carYear") or None
    if car_year in ("", None):
        car_year = None
    else:
        try:
            car_year = int(car_year)
        except (TypeError, ValueError):
            return JsonResponse(
                {"status": "Failed", "message": "car_year must be a number."},
                status=400,
            )

    result = sentiment_for(text)

    review = Review.objects.create(
        dealer_id=dealer_id,
        user=request.user,
        purchase=bool(data.get("purchase")),
        purchase_date=purchase_date,
        car_make=data.get("car_make") or data.get("carMake") or "",
        car_model=data.get("car_model") or data.get("carModel") or "",
        car_year=car_year,
        review=text,
        sentiment=result.get("sentiment", "neutral"),
        sentiment_score=float(result.get("score", 0) or 0),
    )

    payload = review_to_dict(review)
    payload["status"] = "Review added"
    return JsonResponse(payload, status=201)


@csrf_exempt
@require_http_methods(["POST"])
def analyze_review(request):
    """POST /djangoapp/analyze_review -> sentiment for arbitrary text.

    Proxies to the Flask microservice so the UI (and cURL) get the same answer
    as the stored review pipeline.
    """
    data = _body(request)
    text = (data.get("text") or data.get("review") or "").strip()
    if not text:
        return JsonResponse(
            {"error": "Field 'text' is required."}, status=400
        )
    return JsonResponse(sentiment_for(text))


# ---------------------------------------------------------------------------
# Car makes / models
# ---------------------------------------------------------------------------
@require_http_methods(["GET"])
def get_cars(request):
    """GET /djangoapp/get_cars -> all makes with their models."""
    return JsonResponse(car_makes_to_list(), safe=False)
