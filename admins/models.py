from django.db import models
from meal_system import settings


class AdminProfile(models.Model):
    USER_TYPE_CHOICES = [
        ("teacher", "Teacher"),
        ("staff", "Staff"),
    ]

    DESIGNATION_CHOICES = [
        ("lecturer", "Lecturer"),
        ("assistant_professor", "Assistant Professor"),
        ("associate_professor", "Associate Professor"),
        ("professor", "Professor"),
    ]

    HALL_ROLE_CHOICES = [
        ("provost", "Provost"),
        ("assistant_provost", "Assistant Provost"),
        ("house_tutor", "House Tutor"),
        ("office_staff", "Office Staff"),
        ("support_staff", "Support Staff"),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    user_type = models.CharField(
        max_length=20, choices=USER_TYPE_CHOICES, default="teacher"
    )

    name = models.CharField(max_length=100)
    employee_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    designation = models.CharField(
        max_length=50, choices=DESIGNATION_CHOICES, blank=True, null=True
    )  
    hall_role = models.CharField(
        max_length=50, choices=HALL_ROLE_CHOICES, blank=True, null=True
    )
    hall_responsibilities = models.TextField(blank=True, null=True)
    assigned_floor = models.CharField(max_length=20, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    photo = models.ImageField(upload_to="admin_photos/", blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.employee_id})"

    @property
    def is_teacher(self):
        return self.user_type == "teacher"

    @property
    def is_staff_member(self):
        return self.user_type == "staff"
