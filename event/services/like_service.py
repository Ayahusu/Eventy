from django.db import transaction
from event.models import EventLike


class LikeService:

    @staticmethod
    def toggle_like(*, user, event):
        """
        Safely toggles an event like state.
        Returns True if liked, False if unliked.
        """
        # Wrapping in atomic ensures database isolation across concurrent requests
        with transaction.atomic():
            # 1. Let the database handle the race condition. 
            # If it exists, it fetches it. If it doesn't, it atomically creates it.
            like, created = EventLike.objects.get_or_create(
                user=user, 
                event=event
            )

            # 2. If it wasn't created, it means it already existed. 
            # The user's intent on an existing item is to toggle it off (Unlike).
            if not created:
                like.delete()
                return False  # Unliked
            
            return True  # Liked