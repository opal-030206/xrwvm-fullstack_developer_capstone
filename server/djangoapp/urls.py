"""API URL routes, mounted under /djangoapp/."""

from django.urls import path

from . import views

urlpatterns = [
    # Auth
    path("login", views.login_user, name="login"),
    path("logout", views.logout_user, name="logout"),
    path("register", views.register_user, name="register"),
    path("session", views.session_info, name="session"),

    # Dealers
    path("get_dealers", views.get_dealers, name="get_dealers"),
    path("get_dealer/<int:dealer_id>", views.get_dealer_by_id,
         name="get_dealer_by_id"),
    path("get_dealers/<str:state>", views.get_dealers_by_state,
         name="get_dealers_by_state"),
    path("dealers", views.get_dealers, name="dealers"),

    # Reviews
    path("reviews/dealer/<int:dealer_id>", views.get_dealer_reviews,
         name="get_dealer_reviews"),
    path("add_review", views.add_review, name="add_review"),
    path("analyze_review", views.analyze_review, name="analyze_review"),

    # Cars
    path("get_cars", views.get_cars, name="get_cars"),
]
