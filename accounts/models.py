from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("manager", "Manager"),
        ("student", "Student"),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    
    
    def __str__(self):
        return f"{self.username} ({self.role})"
    
    
    @property
    def is_student(self):
        return self.role == "student"
    
    @property
    def is_manager(self):
        return self.role == "manager"
    
    @property
    def is_admin(self):
        return self.role == "admin" or self.is_superuser