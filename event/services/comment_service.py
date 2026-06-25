from event.models import Event, EventComment

from rest_framework.exceptions import ValidationError

class CommentService:

    @staticmethod
    def create_comment(*, user, event_id:int, commnet_text: str) -> EventComment:

        text_stripped = commnet_text.strip()

        if not text_stripped:
                    raise ValidationError("Comment text cannot be empty.")
        
        try:
            event = Event.objects.get_or_create(id=event_id)
        except Event.DoesNotExist:
            raise ValidationError("The event you are trying to comment on does not exist.")

        comment = EventComment.objects.create(
            user=user,
            event=event,
            comment=text_stripped
        )
        
        return comment

            