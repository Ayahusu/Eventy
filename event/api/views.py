from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action

from django.db import transaction

from .serializers import EventSerializer, CommentSerializer
from ..models import Event

from ..services.event_service import EventService
from ..services.like_service import LikeService
from ..services.comment_service import CommentService

from ..selectors.comments import get_comments_for_event

from event.metrics import events_created_total

from drf_spectacular.utils import extend_schema

@extend_schema(tags=['Events API Endpoint'])
class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def create(self, request, *args, **kwargs):
        """
        Creates a new event instance.

        Delegates creation and business logic to EventService to keep 
        the view layer focused purely on HTTP request/response handling.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Delegate creation to the service layer
        event = EventService.create_event(
            user=request.user,
            data=serializer.validated_data
        )
        events_created_total.inc()

        return Response(EventSerializer(event).data, status=status.HTTP_201_CREATED)
    
    def list(self, request, *args, **kwargs):
        """Retrieves a collection of all registered events."""
        queryset = Event.objects.all()

        # Check database level first to avoid unnecessary serialization
        if not queryset.exists():
            return Response({"message": "No Events"})

        serializer = EventSerializer(queryset, many=True)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
            """
            Updates an existing event instance (supports both full and partial updates).

            Delegates update and validation business rules to EventService, keeping
            the view layer focused strictly on HTTP request parsing and response building.
            """
            # Determine if this is a partial update (PATCH) or full update (PUT)
            partial = kwargs.pop('partial', False)
            
            # Retrieve the target event instance (raises HTTP 404 automatically if not found)
            instance = self.get_object()

            # Validate incoming payload against existing instance
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)

            # Delegate update logic and business rules to the service layer
            event = EventService.update_event(
                user=request.user,
                event=instance,
                data=serializer.validated_data,
            )

            # Serialize and return the updated instance with HTTP 200 OK
            return Response(
                self.get_serializer(event).data,
                status=status.HTTP_200_OK
            )
    
    def destroy(self, request, *args, **kwargs):
            """
            Deletes an existing event instance.

            Delegates deletion logic and authorization checks (e.g., verifying if
            the user owns the event or has permission to delete it) to EventService.
            """
            # Retrieve the target event instance (raises HTTP 404 automatically if missing)
            instance = self.get_object()

            # Delegate deletion rules and cleanup to the service layer
            EventService.delete_event(
                user=request.user,
                event=instance
            )

            # Standard DRF response for successful deletion (204 No Content with empty body)
            return Response(
                status=status.HTTP_204_NO_CONTENT
            )

    def retrieve(self, request, *args, **kwargs):
            """
            Retrieves details for a single registered event.

            Uses DRF's self.get_object() to automatically look up the event
            by URL parameter and return a 404 response if it does not exist.
            """
            # Automatically fetches event instance using URL lookup (raises 404 if not found)
            event = self.get_object()

            # Serialize instance using request context for relative URLs/nested fields
            serializer = self.get_serializer(event)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(
            detail=True, 
            methods=['post'],
            permission_classes=[permissions.IsAuthenticated]
    )
    def like_event(self, request, pk=None):
        event = self.get_object()

        is_liked = LikeService.toggle_like(
            event=event,
            user=request.user
        )

        if is_liked:
            return Response(
                {"message": "Liked Post"},
                status=status.HTTP_201_CREATED
            )
                
        return Response(
            {"message": "Unliked Post"},
            status=status.HTTP_200_OK
        )
     
    @action(
        detail=True, 
        methods=['post'], 
        permission_classes=[permissions.IsAuthenticatedOrReadOnly]
    )
    def add_comment(self, request, pk=None):
        event = self.get_object()

        comment = CommentService.create_comment(
                user=request.user,
                event_id=event.id,
                comment_text=request.data.get('comment', '')
            )
        return Response(
                CommentSerializer(comment).data, 
                status=status.HTTP_201_CREATED
            )

        queryset = get_comments_for_event(event_id=event.id)
        serializer = CommentSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)