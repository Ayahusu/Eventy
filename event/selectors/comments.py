from event.models import EventComment

def get_comments_for_event(*, event_id: int):
    """
    Fetches all comments for a specific event, optimized with select_related
    to pull user data in a single database query.
    """
    return EventComment.objects.filter(
        event_id=event_id
    ).select_related(
        'user'
    ).order_by(
        '-create_at'  # Newest comments first
    )