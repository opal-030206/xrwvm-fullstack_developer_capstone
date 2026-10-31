from django.db import models


class CarMake(models.Model):
    """A car manufacturer, e.g. Toyota."""

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class CarModel(models.Model):
    """A model produced by a :class:`CarMake`, e.g. Toyota Camry."""

    car_make = models.ForeignKey(
        CarMake, on_delete=models.CASCADE, related_name="car_models"
    )
    name = models.CharField(max_length=100)
    year = models.PositiveIntegerField()
    body_type = models.CharField(max_length=50, default="Sedan")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        ordering = ["car_make__name", "name"]

    def __str__(self):
        return f"{self.car_make.name} {self.name} ({self.year})"


class Dealer(models.Model):
    """A Cars Dealership branch."""

    full_name = models.CharField(max_length=120)
    short_name = models.CharField(max_length=60)
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=80)
    state = models.CharField(max_length=40, db_index=True)
    zip = models.CharField(max_length=12)
    lat = models.FloatField(default=0)
    long = models.FloatField(default=0)
    image_name = models.CharField(max_length=120, default="dealer-1.jpg")

    class Meta:
        ordering = ["full_name"]

    def __str__(self):
        return self.full_name


class Review(models.Model):
    """A customer review plus the sentiment produced by the Flask service."""

    dealer = models.ForeignKey(
        Dealer, on_delete=models.CASCADE, related_name="reviews"
    )
    user = models.ForeignKey(
        "auth.User", on_delete=models.CASCADE, related_name="reviews"
    )
    purchase = models.BooleanField(default=False)
    purchase_date = models.DateField(null=True, blank=True)
    car_make = models.CharField(max_length=60, blank=True)
    car_model = models.CharField(max_length=60, blank=True)
    car_year = models.PositiveIntegerField(null=True, blank=True)
    review = models.TextField()
    sentiment = models.CharField(max_length=20, default="neutral")
    sentiment_score = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} -> {self.dealer.short_name}"
