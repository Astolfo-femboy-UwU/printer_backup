from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    class Meta:
        app_label = "main_app"

    CARD_TYPE_CHOICES = [
        ("visa", "Visa"),
        ("mastercard", "MasterCard"),
        ("amex", "American Express"),
        ("discover", "Discover"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.TextField(max_length=100, blank=True)
    last_name = models.TextField(max_length=100, blank=True)
    username = models.TextField(max_length=25, blank=True)
    email = models.EmailField(null=True, blank=True)

    # Платёжные данные
    card_number = models.CharField(max_length=19, blank=True)
    expiry_month = models.PositiveIntegerField(null=True, blank=True)
    expiry_year = models.PositiveIntegerField(null=True, blank=True)
    card_holder_name = models.CharField(max_length=100, blank=True)
    billing_address = models.TextField(blank=True)
    card_type = models.CharField(
        max_length=20,
        choices=CARD_TYPE_CHOICES,
        blank=True
    )


class Printer(models.Model):
    class Meta:
        app_label = "main_app"

    description = models.TextField(verbose_name="Описание", blank=True, null=True)
    article = models.CharField(verbose_name="Артикул", blank=True, max_length=100, unique=True)
    price = models.DecimalField(verbose_name="Цена", blank=True, default=0, max_digits=10, decimal_places=2)
    dimensions = models.CharField(verbose_name="Габариты", blank=True, max_length=50, help_text="Формат: ШхГхВ (мм)")
    manufacturer = models.CharField(verbose_name="Производитель", blank=True, max_length=100)

    def __str__(self):
        return f"{self.manufacturer} {self.article}"


class CustomPrinter(models.Model):
    class Meta:
        app_label = "main_app"
