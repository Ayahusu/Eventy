from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

from .api.models import Notification
from .services.notification_service import NotificationService
from .templates_registry import render

@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def send_notification(self, user_id, template, context, channels):
    notifications = NotificationService.create_pending(user_id, template, context, channels)
    for notification in notifications:
        _deliver.delay(notification.id)

@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def _deliver(self, notification_id):
    notification = NotificationService
