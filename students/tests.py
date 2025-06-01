from django.test import TestCase

import pytest
from django.urls import reverse
from django.utils.timezone import localtime, now
from datetime import timedelta
from .models import Student, DailyMealStatus
from accounts.models import CustomUser

# Create your tests here.

@pytest.mark.django_db
def test_update_meal_status(monkeypatch, client):
    user = CustomUser.objects.create_user(username="testuser", password="testtest456")
    student = Student.objects.create(user=user, name="Test", room_number="101")

    # 2. Mock time to before 6 PM
    mock_time = localtime(now()).replace(hour=17, minute=59, second=0)

    monkeypatch.setattr("students.views.now", lambda: mock_time)

    client.login(username="testuser", password="testtest456")
    response = client.post(reverse("update_tomorrow_status"), follow=True)

    # 5. Fetch status object
    tomorrow = mock_time.date() + timedelta(days=1)
    meal_status = DailyMealStatus.objects.get(student=student, date=tomorrow)
    assert response.status_code == 200
    assert meal_status.status in [True, False]
