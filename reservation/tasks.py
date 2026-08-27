from celery import shared_task
from reservation.api.models import Reservation

@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def on_reservation_confirmed(self, reservation_id):
    try:
        reservation = Reservation.objects.select_related("user", "event").get(pk=reservation_id)
    except Reservation.DoesNotExist:
        return

    if reservation.status != Reservation.Status.CONFIRMED:
        return

    from invoicing.tasks import generate_invoice
    from notifications.tasks import send_notification

    generate_invoice.delay(
        user_id=reservation.user_id,
        reference_type="reservation",
        reference_id=reservation.id,
    )
    send_notification.delay(
        user_id=reservation.user_id,
        template="reservation_confirmed",
        context={"event_id": reservation.event_id, "event_name": reservation.event.name},
        channels=["email", "push"],
    )

@shared_task
def expire_stale_reservations():
    """Celery beat schedule: run every minute."""
    from .services import ReservationService
    count = ReservationService.expire_stale_holds()
    return count