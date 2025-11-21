from django.db import models
from datetime import date, timedelta
from meal_system import settings
from django.utils import timezone
import uuid
import qrcode
import base64
from io import BytesIO

from students.models import Student

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
    hall_responsibilities = models.TextField(blank=True, null=True)
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


class SpecialMealRequest(models.Model):
    STATUS_PENDING = "pending"
    STATUS_ACCEPTED = "accepted"
    STATUS_DECLINED = "declined"
    STATUS_COMPLETED = "completed"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_ACCEPTED, "Accepted"),
        (STATUS_DECLINED, "Declined"),
        (STATUS_COMPLETED, "Completed"),
    ]

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="special_requests_created",
    )
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="special_requests_assigned",
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    requested_date = models.DateField()
    meal_type = models.CharField(
        max_length=20,
        choices=[("breakfast", "Breakfast"), ("lunch", "Lunch"), ("dinner", "Dinner")],
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    response_note = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def mark_responded(self, status, note=""):
        self.status = status
        self.response_note = note
        self.responded_at = timezone.now()
        self.save()

    def __str__(self):
        return (
            f"{self.title} ({self.requested_date} - {self.meal_type}) - {self.status}"
        )


class MealToken(models.Model):
    MEAL_CHOICES = [
        ("breakfast", "Breakfast"),
        ("lunch", "Lunch"),
        ("dinner", "Dinner"),
    ]

    TOKEN_TYPE_CHOICES = [
        ("main", "Main Token"),
        ("alternate", "Alternate Token"),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField()
    meal_type = models.CharField(max_length=10, choices=MEAL_CHOICES)
    token_type = models.CharField(max_length=10, choices=TOKEN_TYPE_CHOICES)

    issued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tokens_issued",
    )

    collected = models.BooleanField(default=False)  
    used = models.BooleanField(default=False)  

    issued_at = models.DateTimeField(auto_now_add=True)

    barcode = models.CharField(max_length=50, unique=True, blank=True)
    expiry_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "date", "meal_type"],
                name="unique_token_per_meal_per_day",
            )
        ]
        ordering = ["-issued_at"]


    def generate_qr(self):
        """
        Return QR Code as base64 encoded PNG.
        The encoded payload is a compact, human-readable text with fields:
        STUDENT|MEAL_SLOT|TOKEN_TYPE|DATE|BARCODE
        Example: "Mahfuz Hossain|lunch|main|2025-11-21|A1B2C3D4"
        """

        # Prepare payload fields
        student_name = getattr(self.student, "name", str(self.student))
        meal_slot = self.meal_type  # "breakfast" / "lunch" / "dinner"
        token_type = self.token_type  # "main" / "alternate"
        # Use ISO date for easier parsing
        date_str = self.date.isoformat() if self.date else timezone.localdate().isoformat()
        barcode = self.barcode or ""

        # Compose a compact payload (pipe-separated). Simple and parseable.
        payload = f"{student_name}|{meal_slot}|{token_type}|{date_str}|{barcode}"

        # Create QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(payload)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        img_bytes = buffer.getvalue()

        # Convert to base64 string for embedding in <img src="data:...">
        base64_str = base64.b64encode(img_bytes).decode("utf-8")
        return base64_str

    def save(self, *args, **kwargs):
        from django.utils import timezone
        import uuid

        # Generate barcode only once
        if not self.barcode:
            self.barcode = str(uuid.uuid4())[:12]

        # Auto-set expiry based on meal type
        if not self.expiry_time:
            now = timezone.localtime(
                self.issued_at if self.issued_at else timezone.now()
            )
            if self.meal_type == "breakfast":
                self.expiry_time = now.replace(hour=10, minute=0, second=0)
            elif self.meal_type == "lunch":
                self.expiry_time = now.replace(hour=15, minute=15, second=0)
            elif self.meal_type == "dinner":
                self.expiry_time = now.replace(hour=21, minute=0, second=0)

        super().save(*args, **kwargs)
    
    def is_scanned(self):
        return self.collected is not None

    def __str__(self):
        return f"{self.student.name} - {self.meal_type} ({self.token_type})"
