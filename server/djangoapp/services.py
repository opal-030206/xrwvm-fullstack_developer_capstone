"""Shared helpers: JSON serialisation and the sentiment service client."""

import json
import urllib.error
import urllib.request

from django.conf import settings

from server.sentiment.analyzer import analyze as local_analyze


def dealer_to_dict(dealer):
    return {
        "id": dealer.id,
        "full_name": dealer.full_name,
        "short_name": dealer.short_name,
        "address": dealer.address,
        "city": dealer.city,
        "state": dealer.state,
        "zip": dealer.zip,
        "lat": dealer.lat,
        "long": dealer.long,
        "image": dealer.image_name,
    }


def review_to_dict(review):
    user = review.user
    display_name = (
        f"{user.first_name} {user.last_name}".strip() or user.username
    )
    return {
        "id": review.id,
        "name": display_name,
        "username": user.username,
        "dealership": review.dealer.short_name,
        "dealer_id": review.dealer_id,
        "review": review.review,
        "sentiment": review.sentiment,
        "sentiment_score": review.sentiment_score,
        "purchase": review.purchase,
        "purchase_date": (
            review.purchase_date.isoformat() if review.purchase_date else None
        ),
        "car_make": review.car_make,
        "car_model": review.car_model,
        "car_year": review.car_year,
        "created_at": review.created_at.isoformat(),
    }


def car_makes_to_list():
    from .models import CarMake

    makes = []
    for make in CarMake.objects.prefetch_related("car_models").all():
        makes.append(
            {
                "id": make.id,
                "CarMake": make.name,
                "description": make.description,
                "CarModels": [
                    {
                        "id": model.id,
                        "name": model.name,
                        "year": model.year,
                        "body_type": model.body_type,
                        "price": float(model.price),
                        "dealer_id": None,
                    }
                    for model in make.car_models.all()
                ],
            }
        )
    return makes


def sentiment_for(text):
    """Ask the Flask service first, fall back to the in-process analyser."""
    url = f"{settings.SENTIMENT_SERVICE_URL.rstrip('/')}/analyze"
    payload = json.dumps({"text": text}).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=2.5) as response:
            return json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, OSError, ValueError):
        return local_analyze(text)
