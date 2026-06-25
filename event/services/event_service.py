from event.models import Event
from django.db import transaction

from rest_framework.exceptions import PermissionDenied, ValidationError

class EventService:

    @staticmethod
    @transaction.atomic
    def create_event(user, data):

        if user.role not in ["Organiser", "Admin"]:
            raise PermissionDenied("Only organisers can create events")
        
        if data["end_time"] <= ["start_time"]:
            raise ValidationError("End time must be after start time")
        
        return Event.objects.create(organizer=user, **data)
    
    @staticmethod
    @transaction.atomic
    def update_event(user, event ,data):
        
        if event.organizer != user:
            raise PermissionDenied("You cannot edit this event")
        
        for key, value in data.items():
            setattr(event, key , value)

        event.save()
        return event
    
    @staticmethod
    @transaction.atomic
    def delete_event(user, event):

        if event.organizer != user:
            raise PermissionDenied("You cannot delete this event")
        
        event.soft_delete()

        return event
        
