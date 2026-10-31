"""Page routes served by Django.

``About.html`` and ``Contact.html`` are static pages kept in
``server/frontend/static/``.  Everything else is the React single page app.
"""

from django.urls import path
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import TemplateView

index = ensure_csrf_cookie(TemplateView.as_view(template_name="index.html"))

urlpatterns = [
    path("", index, name="home"),
    path("index.html", index, name="home_index"),

    path("about", TemplateView.as_view(template_name="About.html"),
         name="about"),
    path("about/", TemplateView.as_view(template_name="About.html"),
         name="about_slash"),
    path("contact", TemplateView.as_view(template_name="Contact.html"),
         name="contact"),
    path("contact/", TemplateView.as_view(template_name="Contact.html"),
         name="contact_slash"),

    # React routes
    path("login", index, name="login_page"),
    path("register", index, name="register_page"),
    path("dealer/<int:dealer_id>", index, name="dealer_page"),
    path("postreview/<int:dealer_id>", index, name="postreview_page"),
    path("dealers/<str:state>", index, name="dealers_by_state_page"),
]
