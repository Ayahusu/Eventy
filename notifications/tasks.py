from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

from .api.models import Notification
from .services.notification_service import NotificationService
from .templates_registry import render


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def send_notification(self, user_id, template, context, channels):
    """
    Entry point called by other apps (e.g. reservation).
    Creates PENDING rows immediately, then dispatches per-channel delivery
    tasks so a failure on one channel (e.g. push provider down) doesn't
    block the others (e.g. email still goes out).
    """
    notifications = NotificationService.create_pending(user_id, template, context, channels)
    for notification in notifications:
        _deliver.delay(notification.id)


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def _deliver(self, notification_id):
    try:
        notification = Notification.objects.select_related("user").get(pk=notification_id)
    except Notification.DoesNotExist:
        return

    try:
        if notification.channel == Notification.Channel.EMAIL:
            subject, body = render(notification.template, "email", notification.context)
            send_mail(
                subject=subject,
                message=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[notification.user.email],
            )
        elif notification.channel == Notification.Channel.IN_APP:
            # Row already exists with the rendered context — "sending" an
            # in-app notification just means marking it delivered/visible.
            pass
        elif notification.channel == Notification.Channel.PUSH:
            _send_push(notification)

        NotificationService.mark_sent(notification.id)

    except Exception as exc:
        NotificationService.mark_failed(notification.id, str(exc))
        raise self.retry(exc=exc)


def _send_push(notification):
    """
    Stub — wire up your push provider here (FCM, APNs, OneSignal, etc.)
    once you pick one. Raises until implemented so failures are visible
    rather than silently no-op'd.
    """
    raise NotImplementedError("Push provider not configured yet")