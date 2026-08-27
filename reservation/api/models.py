from django.db import models
from django.utils import timezone

# Create your models here.
class Reservation(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending Payment"
        CONFIRMED = "confirmed", "Confirmed"
        EXPIRED = "expired", "Expired"
        CANCELLED = "cancelled", "Cancelled"

    user = models.ForeignKey()
    event = models.ForeignKey("event.Event", on_delete=models.CASCADE, related_name="reservations")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    held_until = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "event"],
                condition=models.Q(status__in=["pending", "confirmed"]),
                name="unique_active_reservation_per_user_event",
          )           
        ]
        indexes = [
            # Speeds up the expiry sweep: WHERE status='pending' AND held_until < now()
            models.Index(fields=["status", "held_until"]),
        ]

    def __str__(self):
        return f"Reservation({self.user_id}, {self.event_id}, {self.status})"

    @property
    def is_expired(self):
        return(
            self.status == self.Status.PENDING
            and self.held_until is not None
            and self.held_until < timezone.now()
        )