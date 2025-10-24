from django.db import models
from meal_system import settings
from django.utils import timezone

# Create your models here.
class Notice(models.Model):
    title = models.CharField(max_length=200)
    message = models.TextField(blank=True)
    image = models.ImageField(upload_to="notices/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    visible_to_students = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class NoticeViewTracker(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    last_viewed = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - Last Viewed: {self.last_viewed}"
