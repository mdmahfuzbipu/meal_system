from django.db import models

from meal_system import settings


WEEKDAY_CHOICES = [
    ("Monday", "Monday"),
    ("Tuesday", "Tuesday"),
    ("Wednesday", "Wednesday"),
    ("Thursday", "Thursday"),
    ("Friday", "Friday"),
    ("Saturday", "Saturday"),
    ("Sunday", "Sunday"),
]


class WeeklyMenuProposal(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    day_of_week = models.CharField(max_length=10, choices=WEEKDAY_CHOICES)
    breakfast_main = models.CharField(max_length=100, blank=True)
    breakfast_cost = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)

    lunch_main = models.CharField(max_length=100, blank=True)
    lunch_cost = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    lunch_contains_beef = models.BooleanField(default=False)
    lunch_contains_fish = models.BooleanField(default=False)

    dinner_main = models.CharField(max_length=100, blank=True)
    dinner_cost = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    dinner_contains_beef = models.BooleanField(default=False)
    dinner_contains_fish = models.BooleanField(default=False)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    linked_menu = models.ForeignKey(
        "students.WeeklyMenu",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="proposals",
    )

    def __str__(self):
        return f"{self.day_of_week} ({self.status})"
