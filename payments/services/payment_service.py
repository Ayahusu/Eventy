import uuid

from django.db import transaction
from rest_framework.exceptions import ValidationError

from event.models import Registration
from payments.models import Payment


class PaymentService:

    @staticmethod
    def generate_transaction_id():
        return str(uuid.uuid4())

    @staticmethod
    @transaction.atomic
    def initiate_payment(user, event, payment_method):

        try:
            registration = Registration.objects.get(
                user=user,
                event=event
            )
        except Registration.DoesNotExist:
            raise ValidationError(
                "You must register before paying."
            )

        if (
            hasattr(registration, 'payment')
            and registration.payment.status == Payment.PaymentStatus.SUCCESS
        ):
            raise ValidationError(
                "Payment already completed."
            )

        if (
            hasattr(registration, 'payment')
            and registration.payment.status == Payment.PaymentStatus.PENDING
        ):
            return registration.payment

        payment = Payment.objects.create(
            registration=registration,
            amount=event.entry_fee,
            payment_method=payment_method,
            transaction_id=PaymentService.generate_transaction_id(),
            status=Payment.PaymentStatus.PENDING
        )

        return payment