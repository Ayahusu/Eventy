from django.db import transaction
from django.db.models import F
from event.models import Event, Registration
from rest_framework.exceptions import ValidationError

class RegistrationService:
    @staticmethod
    @transaction.atomic
    def register_user(user, event):

        event = Event.objects.select_for_update().get(pk=event.pk)

        if event.status != Event.EventStatus.PUBLISHED:
            raise ValidationError("You can only register for published events.")

        if Registration.objects.filter(user=user, event=event).exists():
            raise ValidationError("You are already registered for this event.")

        if event.max_capacity is not None and event.current_attendance >= event.max_capacity:
            raise ValidationError("Event is full.")

        Registration.objects.create(user=user, event=event)

        Event.objects.filter(pk=event.pk).update(
            current_attendance=F('current_attendance') + 1
        )

        event.refresh_from_db()
        return event
    
    @staticmethod
    @transaction.atomic
    def unregister_user(user, event):

        event = Event.objects.select_for_update().get(pk=event.pk)

        registration = Registration.objects.filter(user=user, event=event).first()
        if not registration:
            raise ValidationError("You are not register for this event")
        
        registration.delete()

        Event.objects.filter(pk=event.pk).update(
            current_attendance=F('current_attendance') - 1
        )
        event.refresh_from_db()
        return event

        