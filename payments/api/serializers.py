from rest_framework import serializers

from payments.models import Payment


class InitiatePaymentSerializer(serializers.Serializer):

    event_id = serializers.UUIDField()

    payment_method = serializers.ChoiceField(
        choices=Payment.PaymentMethod.choices
    )

class VerifyPaymentSerializer(serializers.Serializer):

    transaction_id = serializers.CharField()