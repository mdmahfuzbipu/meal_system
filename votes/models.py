from django.db import models
from django.utils import timezone
from meal_system import settings


class VotePoll(models.Model):
    title = models.CharField(max_length=200)
    question = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="created_polls"
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def is_expired(self):
        return timezone.now() >= self.expires_at

    def total_votes(self):
        return sum(option.votes.count() for option in self.options.all())


class VoteOption(models.Model):
    poll = models.ForeignKey(VotePoll, on_delete=models.CASCADE, related_name="options")
    option_text = models.CharField(max_length=255)

    def __str__(self):
        return self.option_text

    def vote_count(self):
        return self.votes.count()


class Vote(models.Model):
    poll = models.ForeignKey(VotePoll, on_delete=models.CASCADE, related_name="votes")
    option = models.ForeignKey(
        VoteOption, on_delete=models.CASCADE, related_name="votes"
    )
    voted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    voted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("poll", "voted_by")

    def __str__(self):
        return f"{self.voted_by} voted on '{self.poll}'"

    def clean(self):
        # only students can vote
        if hasattr(self.voted_by, "role") and self.voted_by.role != "student":
            from django.core.exceptions import ValidationError

            raise ValidationError("Only students are allowed to vote.")
