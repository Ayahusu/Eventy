import uuid
from django.db import models
from django.db.models import Q
from event.models import Registration

# Create your models here.
class Payment(models.Model):
    class PaymentStatus(models.TextChoices):
        PENDING = "P", "Pending"
        SUCCESS = "S", "Success"
        FAILED = "F", "Failed"
        REFUNDED = "R", "Refunded"
    
    class PaymentMethod(models.TextChoices):
        ESEWA = "E", "Esewa"
        KHALTI = "K", "Khalti"
        STRIPE = "S", "Stripe"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    registration = models.OneToOneField(
        Registration,
        on_delete=models.CASCADE,
        related_name='payments'
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    transaction_id = models.CharField(
        max_length=255,
        unique=True,
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=1,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        db_index=True
    )

    payment_method = models.CharField(
        max_length=1, 
        choices=PaymentMethod.choices, 
    )

    paid_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['status', 'created_at'])
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(amount__get=0),
                name="chk_payment_amount_non_negative"
            )
        ]
    def __str__(self):
        return f"{self.registration.user.email} - {self.get_status_display()}"

    