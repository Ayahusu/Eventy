from rest_framework import viewsets, mixins, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Notification
from ..services.notification_service import NotificationService


class NotificationViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(
            user=self.request.user, channel=Notification.Channel.IN_APP
        ).order_by("-created_at")

    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        found = NotificationService.mark_read(request.user, pk)
        if not found:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response({"message": "Marked as read"}, status=status.HTTP_200_OK)