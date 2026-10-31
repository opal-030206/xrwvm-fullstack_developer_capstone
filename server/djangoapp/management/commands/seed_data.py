"""Seed the database with demo dealers, car makes/models, users and reviews.

    python manage.py seed_data            # idempotent, keeps existing reviews
    python manage.py seed_data --reset    # wipe dealership data first
"""

import datetime
import random

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from server.djangoapp.models import CarMake, CarModel, Dealer, Review
from server.sentiment.analyzer import analyze

DEALERS = [
    # id, full_name, short_name, address, city, state, zip, lat, long, image
    (1, "Kansas City Auto Mall", "KC Auto Mall", "1401 Southwest Blvd",
     "Kansas City", "Kansas", "66103", 39.0812, -94.6107, "dealer-1.jpg"),
    (2, "Wichita Wheels Dealership", "Wichita Wheels", "8250 E Kellogg Dr",
     "Wichita", "Kansas", "67207", 37.6794, -97.2351, "dealer-2.jpg"),
    (3, "Topeka Motor Company", "Topeka Motors", "2300 S Kansas Ave",
     "Topeka", "Kansas", "66611", 39.0261, -95.6793, "dealer-3.jpg"),
    (4, "Gateway St. Louis Motors", "Gateway Motors", "3800 S Kingshighway Blvd",
     "St. Louis", "Missouri", "63109", 38.5989, -90.2755, "dealer-4.jpg"),
    (5, "Lone Star Dallas Autoplex", "Lone Star Autoplex", "9500 N Central Expy",
     "Dallas", "Texas", "75231", 32.8782, -96.7699, "dealer-5.jpg"),
    (6, "Bay Area Auto Gallery", "Bay Area Gallery", "2400 Broadway",
     "Oakland", "California", "94612", 37.8126, -122.2647, "dealer-6.jpg"),
    (7, "Sunshine Miami Motors", "Sunshine Motors", "1750 Biscayne Blvd",
     "Miami", "Florida", "33132", 25.7907, -80.1867, "dealer-1.jpg"),
    (8, "Empire State Auto Group", "Empire Auto", "620 W 51st St",
     "New York", "New York", "10019", 40.7663, -73.9931, "dealer-2.jpg"),
    (9, "Windy City Chicago Cars", "Windy City Cars", "3300 N Ashland Ave",
     "Chicago", "Illinois", "60657", 41.9426, -87.6695, "dealer-3.jpg"),
    (10, "Rocky Mountain Motors", "Rocky Mountain", "700 Colorado Blvd",
     "Denver", "Colorado", "80206", 39.7279, -104.9402, "dealer-4.jpg"),
    (11, "Sooner Oklahoma Autos", "Sooner Autos", "4400 NW Expressway",
     "Oklahoma City", "Oklahoma", "73116", 35.5248, -97.5910, "dealer-5.jpg"),
    (12, "Cornhusker Lincoln Motors", "Cornhusker Motors", "2700 O St",
     "Lincoln", "Nebraska", "68510", 40.8136, -96.6883, "dealer-6.jpg"),
    (13, "Buckeye Cleveland Auto", "Buckeye Auto", "12000 Brookpark Rd",
     "Cleveland", "Ohio", "44130", 41.4184, -81.7823, "dealer-1.jpg"),
    (14, "Desert Sky Phoenix Motors", "Desert Sky Motors", "2200 W Camelback Rd",
     "Phoenix", "Arizona", "85015", 33.5095, -112.1081, "dealer-2.jpg"),
    (15, "Willamette Portland Auto", "Willamette Auto", "1800 NE 122nd Ave",
     "Portland", "Oregon", "97230", 45.5309, -122.5303, "dealer-3.jpg"),
    (16, "Emerald Seattle Motors", "Emerald Motors", "4501 Aurora Ave N",
     "Seattle", "Washington", "98103", 47.6614, -122.3476, "dealer-4.jpg"),
    (17, "Peachtree Atlanta Cars", "Peachtree Cars", "3100 Peachtree Rd NW",
     "Atlanta", "Georgia", "30305", 33.8395, -84.3866, "dealer-5.jpg"),
    (18, "Salina Central Auto", "Salina Central", "900 E Crawford St",
     "Salina", "Kansas", "67401", 38.8411, -97.5981, "dealer-6.jpg"),
]

CAR_MAKES = {
    "Toyota": [
        ("Camry", 2024, "Sedan", "28450"),
        ("Corolla", 2024, "Sedan", "23250"),
        ("RAV4", 2024, "SUV", "31875"),
        ("Tacoma", 2024, "Pickup", "36750"),
    ],
    "Honda": [
        ("Civic", 2024, "Sedan", "24950"),
        ("Accord", 2024, "Sedan", "29500"),
        ("CR-V", 2024, "SUV", "31275"),
    ],
    "Ford": [
        ("F-150", 2024, "Pickup", "42100"),
        ("Mustang", 2024, "Coupe", "45900"),
        ("Escape", 2024, "SUV", "30500"),
    ],
    "Chevrolet": [
        ("Silverado 1500", 2024, "Pickup", "40500"),
        ("Malibu", 2024, "Sedan", "26100"),
        ("Equinox", 2024, "SUV", "29900"),
    ],
    "BMW": [
        ("3 Series", 2024, "Sedan", "47300"),
        ("X5", 2024, "SUV", "68200"),
    ],
    "Tesla": [
        ("Model 3", 2024, "Sedan", "42990"),
        ("Model Y", 2024, "SUV", "47990"),
    ],
    "Hyundai": [
        ("Elantra", 2024, "Sedan", "23100"),
        ("Tucson", 2024, "SUV", "30100"),
    ],
    "Nissan": [
        ("Altima", 2024, "Sedan", "26500"),
        ("Rogue", 2024, "SUV", "30900"),
    ],
}

USERS = [
    # username, password, first, last, email, is_staff, is_superuser
    ("root", "root123", "Root", "Administrator", "root@carsdealership.com",
     True, True),
    ("jdoe", "jdoe123", "John", "Doe", "jdoe@example.com", False, False),
    ("msmith", "msmith123", "Maria", "Smith", "msmith@example.com",
     False, False),
    ("apatel", "apatel123", "Aarav", "Patel", "apatel@example.com",
     False, False),
]

SEED_REVIEWS = [
    (1, "jdoe", True, datetime.date(2024, 3, 18), "Toyota", "Camry", 2023,
     "Fantastic services. The sales team was friendly, patient and explained "
     "every option without pressure. I drove away in a great car at a fair "
     "price."),
    (1, "msmith", False, None, "Honda", "Civic", 2024,
     "Good experience overall. The showroom was clean and the staff were "
     "helpful, though the paperwork took a little longer than expected."),
    (2, "apatel", True, datetime.date(2024, 5, 2), "Ford", "F-150", 2022,
     "Excellent dealership. They honoured the online price and the finance "
     "manager found me a much better rate than my bank offered."),
    (3, "jdoe", False, None, "Tesla", "Model 3", 2024,
     "Average visit. Nothing terrible, but nobody followed up after my test "
     "drive, so I bought elsewhere."),
    (4, "msmith", True, datetime.date(2024, 6, 21), "BMW", "3 Series", 2023,
     "Outstanding service from start to finish. The delivery specialist spent "
     "an hour walking me through every feature of the car."),
    (5, "apatel", True, datetime.date(2024, 7, 9), "Chevrolet", "Silverado 1500",
     2024, "Really happy with my Silverado. The trade-in valuation was fair "
     "and the whole process was smooth and quick."),
    (7, "jdoe", False, None, "Hyundai", "Elantra", 2023,
     "Terrible experience. The car was not ready at the agreed time and the "
     "staff were rude when I asked for an update."),
    (8, "msmith", True, datetime.date(2024, 8, 14), "Nissan", "Rogue", 2024,
     "Great value and a genuinely helpful team. I would recommend this "
     "dealership to anyone shopping for a family SUV."),
    (10, "apatel", False, None, "Toyota", "RAV4", 2024,
     "The buying process was easy and transparent. No hidden fees and the "
     "vehicle was spotless on collection."),
    (12, "jdoe", True, datetime.date(2024, 9, 3), "Honda", "Accord", 2024,
     "Professional and courteous. They arranged financing in under an hour "
     "and even delivered the car to my office."),
    (15, "msmith", False, None, "BMW", "X5", 2023,
     "Disappointing. The used car had an issue the inspection missed and it "
     "took three weeks to get it resolved."),
    (18, "apatel", True, datetime.date(2024, 10, 12), "Ford", "Escape", 2024,
     "Fantastic services once again. Second car I have bought here and the "
     "experience keeps getting better."),
]


class Command(BaseCommand):
    help = "Populate the Cars Dealership database with demo data."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing dealership data before seeding.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["reset"]:
            Review.objects.all().delete()
            Dealer.objects.all().delete()
            CarModel.objects.all().delete()
            CarMake.objects.all().delete()
            self.stdout.write("Cleared existing dealership data.")

        # Dealers -----------------------------------------------------------
        for (dealer_id, full_name, short_name, address, city, state, zip_code,
             lat, long, image) in DEALERS:
            Dealer.objects.update_or_create(
                id=dealer_id,
                defaults={
                    "full_name": full_name,
                    "short_name": short_name,
                    "address": address,
                    "city": city,
                    "state": state,
                    "zip": zip_code,
                    "lat": lat,
                    "long": long,
                    "image_name": image,
                },
            )
        self.stdout.write(f"Dealers: {Dealer.objects.count()}")

        # Car makes and models ---------------------------------------------
        for make_name, models in CAR_MAKES.items():
            make, _ = CarMake.objects.get_or_create(
                name=make_name,
                defaults={"description": f"{make_name} vehicles in stock."},
            )
            for model_name, year, body_type, price in models:
                CarModel.objects.update_or_create(
                    car_make=make,
                    name=model_name,
                    year=year,
                    defaults={"body_type": body_type, "price": price},
                )
        self.stdout.write(
            f"Car makes: {CarMake.objects.count()} "
            f"({CarModel.objects.count()} models)"
        )

        # Users -------------------------------------------------------------
        for username, password, first, last, email, staff, superuser in USERS:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "first_name": first,
                    "last_name": last,
                    "email": email,
                    "is_staff": staff,
                    "is_superuser": superuser,
                },
            )
            if created:
                user.set_password(password)
                user.save()
        self.stdout.write(f"Users: {User.objects.count()}")

        # Reviews -----------------------------------------------------------
        if not Review.objects.exists():
            for (dealer_id, username, purchase, purchase_date, car_make,
                 car_model, car_year, text) in SEED_REVIEWS:
                result = analyze(text)
                Review.objects.create(
                    dealer_id=dealer_id,
                    user=User.objects.get(username=username),
                    purchase=purchase,
                    purchase_date=purchase_date,
                    car_make=car_make,
                    car_model=car_model,
                    car_year=car_year,
                    review=text,
                    sentiment=result["sentiment"],
                    sentiment_score=result["score"],
                )
            self.stdout.write(f"Reviews: {Review.objects.count()}")
        else:
            self.stdout.write(
                f"Reviews: {Review.objects.count()} (left untouched)"
            )

        # Keep random reproducible for callers that rely on it.
        random.seed(2024)
        self.stdout.write(self.style.SUCCESS("Database seeded successfully."))
