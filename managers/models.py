from django.db import models
from datetime import date, timedelta
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


class ManagerProfile(models.Model):
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    nid = models.CharField(max_length=30, unique=True)
    phone_number = models.CharField(max_length=20)
    emergency_phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    profile_picture = models.ImageField(
        upload_to="manager_profiles/", blank=True, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.full_name} ({self.user.username})"



class WeeklyMenuProposal(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    day_of_week = models.CharField(max_length=10, choices=WEEKDAY_CHOICES)
    week_start_date = models.DateField(default=date.today)  

    # Breakfast
    breakfast_main = models.CharField(max_length=100, blank=True)
    breakfast_cost = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)

    # Lunch
    lunch_main = models.CharField(max_length=100, blank=True)
    lunch_cost = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    lunch_contains_beef = models.BooleanField(default=False)
    lunch_contains_fish = models.BooleanField(default=False)

    lunch_alternate = models.CharField(max_length=100, blank=True)
    lunch_cost_alternate = models.DecimalField(
        max_digits=6, decimal_places=2, default=0.00
    )

    # Dinner
    dinner_main = models.CharField(max_length=100, blank=True)
    dinner_cost = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    dinner_contains_beef = models.BooleanField(default=False)
    dinner_contains_fish = models.BooleanField(default=False)

    dinner_alternate = models.CharField(max_length=100, blank=True)
    dinner_cost_alternate = models.DecimalField(
        max_digits=6, decimal_places=2, default=0.00
    )

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
        return f"{self.day_of_week} ({self.status}) - Week of {self.week_start_date}"

    @staticmethod
    def get_week_start():
        """Return Monday of current week."""
        today = date.today()
        return today - timedelta(days=today.weekday())
