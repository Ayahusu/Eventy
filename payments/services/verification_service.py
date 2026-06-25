from django.db import transaction
from django.db.models import F
from django.utils import timezone

from event.models import Registration, Event
from payments.models import Payment

from rest_framework.exceptions import ValidationError

class VerificationService:

    @staticmethod
    @transaction.atomic
    def verify_payment(user, event):
        payment = Payment.objects.select_for_update().get(
            pk=payment.pk
        )

        if payment.status == Payment.PaymentStatus.SUCCESS:
            return payment
        
        if payment.status == Payment.PaymentStatus.FAILED:
            raise ValidationError(
                "Failed payments cannot be verified."
            )
        
        registration = payment.registration
        event = registration.event

        event = Event.objects.select_for_update().get(
            pk=event.pk
        )

        if (
            event.max_capacity is not None
            and event.current_attendance >= event.max_capacity
        ):
            raise ValidationError(
                "Event is full."
            )
        
        payment.status = Payment.PaymentStatus.SUCCESS
        payment.paid_at = timezone.now()
        payment.save(
            update_fields=['status', 'paid_at']
        )

        # ✅ Confirm registration
        registration.status = Registration.RegistrationStatus.CONFIRMED
        registration.save(update_fields=['status'])

        # ✅ Increment attendance safely
        Event.objects.filter(pk=event.pk).update(
            current_attendance=F('current_attendance') + 1
        )

        return payment
        