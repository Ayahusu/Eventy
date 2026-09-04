from ..api.models import Notification


class NotificationService:
    @staticmethod
    def create_pending(user_id, template, context, channels):
        """
        Creates one Notification row per requested channel, all PENDING.
        Actual sending happens asynchronously via tasks — this just
        records intent so nothing is lost if a worker crashes mid-send.
        """
        notifications = [
            Notification(user_id=user_id, channel=channel, template=template, context=context)
            for channel in channels
        ]
        return Notification.objects.bulk_create(notifications)

    @staticmethod
    def mark_sent(notification_id):
        from django.utils import timezone
        Notification.objects.filter(pk=notification_id).update(
            status=Notification.Status.SENT, sent_at=timezone.now()
        )

    @staticmethod
    def mark_failed(notification_id, reason):
        Notification.objects.filter(pk=notification_id).update(
            status=Notification.Status.FAILED, failure_reason=reason[:500]
        )

    @staticmethod
    def mark_read(user, notification_id):
        from django.utils import timezone
        from django.utils import timezone as tz
        updated = Notification.objects.filter(
            pk=notification_id, user=user, channel=Notification.Channel.IN_APP
        ).update(read_at=tz.now())
        return updated > 0