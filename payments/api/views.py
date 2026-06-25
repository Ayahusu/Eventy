from rest_framework import status, permissions, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from event.models import Event
from payments.models import Payment

from payments.api.serializers import (
    InitiatePaymentSerializer,
    VerifyPaymentSerializer
)

from payments.services.payment_service import PaymentService
from payments.services.verification_service import VerificationService


class PaymentViewSet(viewsets.ViewSet):

    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'])
    def initiate(self, request):

        serializer = InitiatePaymentSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        event = Event.objects.get(
            pk=serializer.validated_data['event_id']
        )

        payment = PaymentService.initiate_payment(
            user=request.user,
            event=event,
            payment_method=serializer.validated_data['payment_method']
        )

        return Response(
            {
                "payment_id": payment.id,
                "transaction_id": payment.transaction_id,
                "status": payment.status
            },
            status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=['post'])
    def verify(self, request):

        serializer = VerifyPaymentSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        payment = Payment.objects.get(
            transaction_id=serializer.validated_data['transaction_id']
        )

        payment = VerificationService.verify_payment(
            payment=payment
        )

        return Response(
            {
                "message": "Payment verified successfully",
                "payment_status": payment.status
            },
            status=status.HTTP_200_OK
        )