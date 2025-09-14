from django.core.management.base import BaseCommand
from students.utils import generate_monthly_summary_for_all
from datetime import date


class Command(BaseCommand):
    help = "Generate monthly meal summary for all students"

    def handle(self, *args, **kwargs):
        today = date.today()
        year = today.year
        month = today.month - 1 if today.month > 1 else 12
        if today.month == 1:
            year -= 1  # Adjust for January

        self.stdout.write(f"Generating summary for {year}-{str(month).zfill(2)}...")
        generate_monthly_summary_for_all(year, month)
        self.stdout.write(self.style.SUCCESS("Monthly summary generated successfully!"))
