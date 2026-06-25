from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action

from .serializers import EventSerializer, CommentSerializer
from ..models import Event

from ..services.event_service import EventService
from ..services.registration_service import RegistrationService
from ..services.like_service import LikeService
from ..services.comment_service import CommentService

from ..selectors.comments import get_comments_for_event



class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        event = EventService.create_event(
            user=request.user,
            data=serializer.validated_data
        )

        return Response(EventSerializer(event).data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        event = EventService.update_event(
            user=request.user,
            event=instance,
            data=serializer.validated_data,
        )

        return Response(
            EventSerializer(event).data,
            status=status.HTTP_200_OK
            )
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        EventService.delete_event(
            user=request.user,
            event=instance
        )

        return Response(
            {"message": "Event deleted successfully"},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def register(self, request, pk=None):
        event = self.get_object()

        RegistrationService.register_user(
            user=request.user,
            event=event
        )
        return Response({"message": "Registered successfully"})
    
    @action(detail=True, methods=['DELETE'], permission_classes=[permissions.IsAuthenticated])
    def unregister(self, request, pk=None):
        event = self.get_object()

        RegistrationService.unregister_user(
            event=event,
            user=request.user
        )

        return Response(
            {"message": "Unregistered successfully"},
            status=status.HTTP_200_OK
        )
    
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
        methods=['get', 'post'], 
        permission_classes=[permissions.IsAuthenticatedOrReadOnly]
    )
    def comments(self, request, pk=None):
        """
        GET  /api/events/{id}/comments/ -> View all comments using a Selector
        POST /api/events/{id}/comments/ -> Add a comment using a Service
        """
        event = self.get_object()

        if request.method == 'POST':
            # Ensure an unauthenticated user can't hit the POST sub-route
            if not request.user.is_authenticated:
                return Response(status=status.HTTP_401_UNAUTHORIZED)

            comment = CommentService.create_comment(
                user=request.user,
                event_id=event.id,
                comment_text=request.data.get('comment', '')
            )
            return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)

        # GET Request: Fetch comments via our Selector
        queryset = get_comments_for_event(event_id=event.id)
        serializer = CommentSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)