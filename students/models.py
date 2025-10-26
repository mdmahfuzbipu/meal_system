from django.db import models
from django.conf import settings
import calendar

# Create your models here.

DEPARTMENT_CHOICES = [
    ("ICE", "ICE"),
    ("EEE", "EEE"),
    ("CIVIL", "CIVIL"),
    ("CSE", "CSE"),
    ("ME", "ME"),
    ("LLB", "LLB"),
    ("ELL", "ELL"),
    ("BBA", "BBA"),
]

BLOOD_GROUP_CHOICES = [
    ("A+", "A+"),
    ("A-", "A-"),
    ("B+", "B+"),
    ("B-", "B-"),
    ("O+", "O+"),
    ("O-", "O-"),
    ("AB+", "AB+"),
    ("AB-", "AB-"),
]

WEEKDAY_CHOICES = [
    ("Monday", "Monday"),
    ("Tuesday", "Tuesday"),
    ("Wednesday", "Wednesday"),
    ("Thursday", "Thursday"),
    ("Friday", "Friday"),
    ("Saturday", "Saturday"),
    ("Sunday", "Sunday"),
]


class Student(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=40)
    room_number = models.CharField(max_length=5)
    default_meal_status = models.BooleanField(default=True)
    default_prefers_beef = models.BooleanField(default=True)
    default_prefers_fish = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    
    def __str__(self):
        return f"{self.name} (Room {self.room_number})"


class StudentDetails(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE)
    university_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=5,choices=DEPARTMENT_CHOICES)  
    batch = models.CharField(max_length=4) #20th
    date_of_birth = models.DateField()
    national_id = models.CharField(max_length=20, unique=True)
    address = models.TextField(blank=True)
    phone_number = models.CharField(max_length=16)
    email = models.EmailField(max_length=100, blank=True, null=True)
    blood_group = models.CharField(max_length=3,choices=BLOOD_GROUP_CHOICES)
    guardian_name = models.CharField(max_length=40)
    guardian_phone = models.CharField(max_length=16)
    profile_picture = models.ImageField(upload_to="profile_pics/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class StudentMealPreference(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    month = models.CharField(max_length=7) # format: YYYY-MM
    prefers_beef = models.BooleanField(default=True)
    prefers_fish = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['student', 'month'], name='unique_student_month_preference')
        ]

    def get_month_display_name(self):
        return f"{calendar.month_name[self.month]}"


class WeeklyMenu(models.Model):
    day_of_week = models.CharField(max_length=10, choices=WEEKDAY_CHOICES, unique=True)

    # Breakfast
    breakfast_main = models.CharField(max_length=100, blank=True)
    breakfast_cost = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    
    # breakfast_alternate = models.CharField(max_length=100, blank=True)
    # breakfast_cost_alternate = models.DecimalField(
    #     max_digits=6, decimal_places=2, default=0.00
    # )


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
    

    def __str__(self):
        return self.day_of_week


class DailyMealStatus(models.Model):
    student = models.ForeignKey("Student", on_delete=models.CASCADE)
    date = models.DateField()
    
    breakfast_on = models.BooleanField(default=True)
    lunch_on = models.BooleanField(default=True)
    dinner_on = models.BooleanField(default=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "date"], name="unique_meal_status_per_day"
            )
        ]
        ordering = ['-date']

    def __str__(self):
        return f"{self.student.name} - {self.date} - {'ON' if self.status else 'OFF'}"


class DailyMealCost(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField()
    total_cost = models.DecimalField(max_digits=6, decimal_places=2)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['student', 'date'], name='unique_meal_cost_per_day')
        ]

    def __str__(self):
        return f"{self.student.name} - {self.date} - {self.total_cost} Taka"


class MonthlyMealSummary(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    month = models.CharField(max_length=7)  # Format: YYYY-MM
    total_cost = models.DecimalField(max_digits=8, decimal_places=2)
    total_on_days = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['student', 'month'], name='unique_monthly_summary')
        ]

    def __str__(self):
        return f"{self.student.name} - {self.month} - Total: {self.total_cost} Taka"


class Complaint(models.Model):
    student = models.ForeignKey("Student", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    room_number = models.CharField(max_length=10)
    phone_number = models.CharField(max_length=15)
    description = models.TextField()
    is_fixed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    fixed_at = models.DateTimeField(null=True, blank=True)
    fixed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="fixed_complaints",
    )

    def __str__(self):
        return f"{self.name} - {self.room_number} ({'Fixed' if self.is_fixed else 'Pending'})"


from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import date


from .utils import save_daily_cost

@receiver(post_save, sender=DailyMealStatus)
def update_daily_cost(sender, instance, **kwargs):
    """
    Automatically calculate and save cost when meal status is updated.
    """
    save_daily_cost(instance.student, instance.date)


class WeeklyMenuReview(models.Model):
    MEAL_CHOICES = [
        ("breakfast", "Breakfast"),
        ("lunch", "Lunch"),
        ("dinner", "Dinner"),
    ]

    WEEKDAY_CHOICES = [
        ("Monday", "Monday"),
        ("Tuesday", "Tuesday"),
        ("Wednesday", "Wednesday"),
        ("Thursday", "Thursday"),
        ("Friday", "Friday"),
        ("Saturday", "Saturday"),
        ("Sunday", "Sunday"),
    ]

    student = models.ForeignKey("students.Student", on_delete=models.CASCADE)
    day_of_week = models.CharField(max_length=10, choices=WEEKDAY_CHOICES)
    meal_type = models.CharField(max_length=10, choices=MEAL_CHOICES)
    rating = models.PositiveSmallIntegerField(
        choices=[(i, str(i)) for i in range(1, 6)]
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "day_of_week", "meal_type")
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"{self.student.name} - {self.day_of_week} {self.meal_type}: {self.rating}"
        )
