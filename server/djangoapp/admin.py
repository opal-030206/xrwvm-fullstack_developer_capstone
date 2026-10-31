from django.contrib import admin

from .models import CarMake, CarModel, Dealer, Review


class CarModelInline(admin.TabularInline):
    model = CarModel
    extra = 1


@admin.register(CarMake)
class CarMakeAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)
    inlines = [CarModelInline]


@admin.register(CarModel)
class CarModelAdmin(admin.ModelAdmin):
    list_display = ("name", "car_make", "year", "body_type", "price")
    list_filter = ("car_make", "body_type", "year")
    search_fields = ("name",)


@admin.register(Dealer)
class DealerAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "city", "state", "zip")
    list_filter = ("state",)
    search_fields = ("full_name", "city", "state")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "dealer",
        "user",
        "sentiment",
        "purchase",
        "created_at",
    )
    list_filter = ("sentiment", "purchase", "dealer")
    search_fields = ("review", "user__username", "dealer__full_name")
