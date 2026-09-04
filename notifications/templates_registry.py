"""
Maps a template key to functions that render the subject/body for email
and the display text for in-app/push. Add new templates here only.
"""

TEMPLATES = {
    "reservation_confirmed": {
        "email_subject": lambda ctx: f"You're confirmed for {ctx['event_name']}!",
        "email_body": lambda ctx: (
            f"Hi! Your reservation for {ctx['event_name']} is confirmed. "
            f"Your invoice will follow shortly."
        ),
        "short_text": lambda ctx: f"Reservation confirmed for {ctx['event_name']}",
    },
    "reservation_expired": {
        "email_subject": lambda ctx: f"Your hold for {ctx['event_name']} has expired",
        "email_body": lambda ctx: (
            f"Your 10-minute hold for {ctx['event_name']} expired before payment "
            f"was completed. You can try reserving again if seats are available."
        ),
        "short_text": lambda ctx: f"Hold expired for {ctx['event_name']}",
    },
}


def render(template, channel, context):
    from .exceptions import TemplateNotFound
    if template not in TEMPLATES:
        raise TemplateNotFound(template)

    spec = TEMPLATES[template]
    if channel == "email":
        return spec["email_subject"](context), spec["email_body"](context)
    return spec["short_text"](context)