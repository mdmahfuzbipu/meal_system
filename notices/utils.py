from .models import Notice, NoticeViewTracker


def get_unread_notice_count(user):
    if not user.is_authenticated:
        return 0

    try:
        tracker = NoticeViewTracker.objects.get(user=user)
        return Notice.objects.filter(created_at__gt=tracker.last_viewed).count()
    except NoticeViewTracker.DoesNotExist:
        return Notice.objects.count() 
