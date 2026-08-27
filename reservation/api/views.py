from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from event.models import Event
from ..services.reservation_seervice import ReservationService
# Create your views here.

class ReservationViewSet(viewsets.GenericViewSet):
    queryset = Event.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=["post"])
    def reserve(self, request, pk=None):
        event = self.get_object()
        reservation = ReservationService.hold_seat(user=request.user, event=event)
        return Response(
             {
                "message": "Seat reserved",
                "reservation_id": reservation.id,
                "held_until": reservation.held_until,
            },
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=["delete"])
    def cancel(self, request, pk=None):
        event = self.get_object()
        ReservationService.cancel(user=request.user, event=evnt)
        return Response({"message": "Reservation cancelled"}, status=status.HTTP_200_OK)
    