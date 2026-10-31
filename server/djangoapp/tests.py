"""Tests for the Cars Dealership JSON API and page routes.

Run with::

    python manage.py test

The CI workflow in ``.github/workflows/ci.yml`` runs exactly this suite.
"""

import datetime

from django.contrib.auth.models import User
from django.test import TestCase

from .models import CarMake, CarModel, Dealer, Review


class DealershipApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.kansas = Dealer.objects.create(
            full_name="Kansas City Auto Mall",
            short_name="KC Auto Mall",
            address="1401 Southwest Blvd",
            city="Kansas City",
            state="Kansas",
            zip="66103",
            lat=39.0812,
            long=-94.6107,
            image_name="dealer-1.jpg",
        )
        cls.texas = Dealer.objects.create(
            full_name="Austin Auto Gallery",
            short_name="Austin Auto",
            address="900 Congress Ave",
            city="Austin",
            state="Texas",
            zip="78701",
            lat=30.2672,
            long=-97.7431,
            image_name="dealer-2.jpg",
        )
        cls.user = User.objects.create_user(
            username="root",
            password="root123",
            first_name="Root",
            last_name="Administrator",
            email="root@carsdealership.com",
        )
        cls.make = CarMake.objects.create(name="Toyota", description="Japanese")
        CarModel.objects.create(
            car_make=cls.make,
            name="Camry",
            year=2024,
            body_type="Sedan",
            price=28000,
        )
        Review.objects.create(
            dealer=cls.kansas,
            user=cls.user,
            purchase=True,
            purchase_date=datetime.date(2026, 10, 20),
            car_make="Toyota",
            car_model="Camry",
            car_year=2024,
            review="Fantastic services",
            sentiment="positive",
            sentiment_score=3.4,
        )

    # -- dealers ---------------------------------------------------------
    def test_get_dealers_returns_every_branch(self):
        response = self.client.get("/djangoapp/get_dealers")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(len(payload), 2)
        self.assertEqual(payload[0]["full_name"], "Austin Auto Gallery")

    def test_get_dealer_by_id(self):
        response = self.client.get(f"/djangoapp/get_dealer/{self.kansas.id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["state"], "Kansas")

    def test_get_dealer_by_id_missing(self):
        response = self.client.get("/djangoapp/get_dealer/9999")
        self.assertEqual(response.status_code, 404)

    def test_get_dealers_by_state(self):
        response = self.client.get("/djangoapp/get_dealers/Kansas")
        payload = response.json()
        self.assertEqual(len(payload), 1)
        self.assertEqual(payload[0]["short_name"], "KC Auto Mall")

    def test_get_dealers_by_state_is_case_insensitive(self):
        response = self.client.get("/djangoapp/get_dealers/texas")
        self.assertEqual(len(response.json()), 1)

    # -- reviews ---------------------------------------------------------
    def test_reviews_for_dealer(self):
        response = self.client.get(
            f"/djangoapp/reviews/dealer/{self.kansas.id}"
        )
        payload = response.json()
        self.assertEqual(len(payload), 1)
        self.assertEqual(payload[0]["sentiment"], "positive")
        self.assertEqual(payload[0]["username"], "root")

    def test_reviews_for_unknown_dealer(self):
        response = self.client.get("/djangoapp/reviews/dealer/9999")
        self.assertEqual(response.status_code, 404)

    def test_add_review_requires_login(self):
        response = self.client.post(
            "/djangoapp/add_review",
            data={"dealer_id": self.texas.id, "review": "Great place"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)

    def test_add_review_stores_sentiment(self):
        self.client.login(username="root", password="root123")
        response = self.client.post(
            "/djangoapp/add_review",
            data={
                "dealer_id": self.texas.id,
                "review": "Fantastic services",
                "purchase": True,
                "purchase_date": "2026-10-20",
                "car_make": "Toyota",
                "car_model": "Camry",
                "car_year": 2024,
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertEqual(body["sentiment"], "positive")
        self.assertEqual(Review.objects.filter(dealer=self.texas).count(), 1)

    # -- car makes -------------------------------------------------------
    def test_get_cars_groups_models_under_makes(self):
        response = self.client.get("/djangoapp/get_cars")
        payload = response.json()
        self.assertEqual(len(payload), 1)
        self.assertEqual(payload[0]["CarMake"], "Toyota")
        self.assertEqual(payload[0]["CarModels"][0]["name"], "Camry")

    # -- auth ------------------------------------------------------------
    def test_login_and_session(self):
        self.assertFalse(self.client.get("/djangoapp/session").json()["loggedIn"])
        response = self.client.post(
            "/djangoapp/login",
            data={"userName": "root", "password": "root123"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "Authenticated")
        self.assertTrue(self.client.get("/djangoapp/session").json()["loggedIn"])

    def test_login_with_bad_password(self):
        response = self.client.post(
            "/djangoapp/login",
            data={"userName": "root", "password": "wrong"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["status"], "Authentication failed")

    def test_logout(self):
        self.client.login(username="root", password="root123")
        response = self.client.post("/djangoapp/logout")
        self.assertEqual(response.json()["status"], "Logged out")
        self.assertFalse(self.client.get("/djangoapp/session").json()["loggedIn"])

    def test_register_creates_account(self):
        response = self.client.post(
            "/djangoapp/register",
            data={
                "userName": "newdriver",
                "firstName": "New",
                "lastName": "Driver",
                "email": "new.driver@example.com",
                "password": "s3cret-pass",
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.filter(username="newdriver").exists())

    def test_register_rejects_duplicate_username(self):
        response = self.client.post(
            "/djangoapp/register",
            data={
                "userName": "root",
                "firstName": "Root",
                "lastName": "Again",
                "email": "root2@example.com",
                "password": "root123",
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 409)

    def test_register_requires_all_five_fields(self):
        response = self.client.post(
            "/djangoapp/register",
            data={"userName": "partial"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("First Name", response.json()["message"])

    # -- sentiment -------------------------------------------------------
    def test_analyze_review_returns_positive_sentiment(self):
        response = self.client.post(
            "/djangoapp/analyze_review",
            data={"text": "Fantastic services"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["sentiment"], "positive")
        self.assertGreater(body["score"], 0)

    def test_analyze_review_requires_text(self):
        response = self.client.post(
            "/djangoapp/analyze_review", data={}, content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)


class PageRouteTests(TestCase):
    def test_home_page_renders(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cars Dealership")

    def test_about_page_renders(self):
        response = self.client.get("/about")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "About Us")

    def test_contact_page_renders(self):
        response = self.client.get("/contact")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Contact Us")

    def test_react_routes_render_the_single_page_app(self):
        for path in ("/login", "/register", "/dealer/1", "/postreview/1",
                     "/dealers/Kansas"):
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 200)
