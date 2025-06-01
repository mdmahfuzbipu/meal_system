from django.db import models
from django.conf import settings

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
    

class WeeklyMenu(models.Model):
    day_of_week = models.CharField(max_length=10, choices=WEEKDAY_CHOICES, unique=True)
    meal_items = models.TextField()
    
    includes_beef = models.BooleanField(default=False)
    includes_fish = models.BooleanField(default=True)

    base_cost = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    alternate_cost = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.day_of_week} Item -{self.meal_items} - Cost {self.base_cost}Taka/{self.alternate_cost}Taka"


class DailyMealStatus(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.BooleanField(default=True)  
    created_at = models.DateTimeField(auto_now_add=True)

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