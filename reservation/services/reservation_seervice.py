from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from event.models import Event
from reservation.api.models import Reservation
from ..exceptions import EventNotOpenForReservation, AlreadyReserved, EventFull, ReservationNotFound

HOLD_DURATION = timedelta(minutes=getattr(settings, "RESERVATION_HOLD_MINUTES", 10))

class ReservationService:
    @staticmethod
    @transaction.atomic
    def hold_seat(user, event):

        event = Event.objects.select_for_update().get(pk=event.pk)

        if event.status != event.EventStatus.PUBLISHED:
            raise EventNotOpenForReservation()

        if Reservation.objects.filter(
            user=user, event=event, status__in=[Reservation.Status.PENDING, Reservation.Status.CONFIRMED]
        ).exists():
            raise AlreadyReserved()

        active_count = Reservation.objects.filter(
            event=event, status__in=[Reservation.Status.PENDING, Reservation.Status.CONFIRMED]
        ).count()

        if event.max_capacity is not None and active_count >= event.max_capacity:
            raise EventFull()

        reservation = Reservation.objects.create(
            user=user,
            event=event,
            status=Reservation.Status.PENDING,
            held_until= timezone() + HOLD_DURATION,
        )

        return reservation

    @staticmethod
    @transaction.atomic
    def confirm(reservation_id):
        reservation = Reservation.objects.select_for_update().get(pk=reservation_id)

        if reservation.status == Reservation.Status.CONFIRMED:
            return reservation

        if reservation.status != Reservation.Status.PENDING:
            raise EventNotOpenForReservation(
                detail=f"Reservation is {reservation.status}, cannot confirm."
            )

        reservation.status = Reservation.Status.CONFIRMED
        reservation.held_until = None
        reservation.save(update_fields=["status", "held_util","updated_at"])

        transaction.on_commit(lambda: _dispatch_confirmation_tasks(reservation.id))

        return reservation

    @staticmethod
    @transaction.atomic
    def cancel(user, event):
        reservation = Reservation.objects.select_for_update().filter(
            user=user,
            event=event,
            status__in=[Reservation.Status.PENDING, Reservation.Status.CONFIRMED]
        ).first()

        if not reservation:
            raise ReservationNotFound()

        reservation.status = Reservation.Status.CANCELLED
        reservation.save(update_fields=["status", "updated_at"])
        return reservation

    @staticmethod
    def expire_stale_holds():
        now = timezone.now()
        stale_ids = list(
            Reservation.objects.filter(
                status=Reservation.Status.PENDING, held_until__lt=now
            ).values_list("id", flat=True)
        )

        with transaction.atomic():
            Reservation.objects.select_for_update().filter(
                id__in=stale_ids, status=Reservation.Status.PENDING
            ).update(status=Reservation.Status.EXPIRED, held_until=None)

        return len(stale_ids)

def _dispatch_confirmation_tasks(reservation_id):
        from ..tasks import on_reservation_confirmed
        on_reservation_confirmed.delay(reservation_id)