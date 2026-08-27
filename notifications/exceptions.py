class TemplateNotFound(Exception):
    """Raised when a notification template key has no registered renderer."""
    pass

class UnsupportedChannel(Exception):
    """Raised when a channel isn't one of the supported delivery mechanisms."""
    pass
