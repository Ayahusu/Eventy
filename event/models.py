from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Q, F
from django.utils import timezone
from django.utils.text import slugify
import uuid
from users.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)
    # IMPROVED: Let DB enforce uniqueness, no manual loop (avoid race condition)
    slug = models.SlugField(unique=True, db_index=True, blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        # Only regenerate slug if name changed (or new object)
        if not self.pk or self.name != Category.objects.get(pk=self.pk).name:
            self.slug = slugify(self.name)
            # If slug is empty after slugify (e.g., name is only special chars), handle gracefully
            if not self.slug:
                self.slug = f"cat-{self.pk or 'new'}"
            # Django's unique constraint will raise IntegrityError on collision.
            # For a production app, consider django-autoslug or a retry loop with transaction.
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('category_detail', kwargs={'slug': self.slug})

class EventManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

class Event(models.Model):
    class EventType(models.TextChoices):
        ONLINE = 'O', 'Online'
        OFFLINE = 'OF', 'Offline'
        HYBRID = 'H', 'Hybrid'

    class EventStatus(models.TextChoices):
        DRAFT = 'D', 'Draft'
        PUBLISHED = 'P', 'Published'
        CANCELLED = 'C', 'Cancelled'
        COMPLETED = 'CM', 'Completed'

    # 1. Primary Key & Relations
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organizer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='events',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='events'
    )

    # 2. Information Fields
    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField()
    event_type = models.CharField(max_length=2, choices=EventType.choices, default=EventType.ONLINE)
    banner_image = models.ImageField(upload_to='events/%Y/%m/', null=True, blank=True)

    # 3. Logistics
    location = models.CharField(max_length=255, blank=True)
    address = models.TextField(blank=True)
    meeting_link = models.URLField(blank=True)

    # 4. Temporal Fields
    start_time = models.DateTimeField(db_index=True)
    end_time = models.DateTimeField(db_index=True)

    # 5. Financials & Capacity
    entry_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    max_capacity = models.PositiveIntegerField(null=True, blank=True)
    current_attendance = models.PositiveIntegerField(default=0)

    # 6. Status & Metadata
    status = models.CharField(
        max_length=2,
        choices=EventStatus.choices,
        default=EventStatus.DRAFT,
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = EventManager()
    all_objects = models.Manager()

    class Meta:
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['status', '-start_time'], name='status_start_desc_idx'),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(current_attendance__gte=0),
                name="attendance_non_negative"
            ),
            models.CheckConstraint(
                condition=Q(max_capacity__isnull=True) | Q(current_attendance__lte=F("max_capacity")),
                name="attendance_within_capacity"
            ),
            models.CheckConstraint(
                condition=Q(entry_fee__gte=0),
                name="entry_fee_non_negative"
            ),
        ]

    def clean(self):
        super().clean()

        # 1. Capacity validations
        if self.max_capacity is not None:
            if self.current_attendance < 0:
                raise ValidationError("Attendance cannot be negative")
            if self.current_attendance > self.max_capacity:
                raise ValidationError("Attendance cannot exceed capacity")

        # 2. Time validations
        if self.start_time and self.end_time:
            if self.start_time >= self.end_time:
                raise ValidationError({"end_time": "The end time must be after the start time."})

            # IMPROVED: Past start_time validation for both create AND update
            # (but allow if status is DRAFT or CANCELLED? adjust as needed)
            if self.start_time < timezone.now():
                # Option: only block for PUBLISHED events
                if self.status == self.EventStatus.PUBLISHED:
                    raise ValidationError({"start_time": "Cannot set a published event's start time in the past."})
                # Or if you want to block all: raise unconditionally

        # 3. ADDED: Logistics validation based on event type
        if self.event_type == self.EventType.ONLINE:
            if not self.meeting_link:
                raise ValidationError({"meeting_link": "Online events require a meeting link."})
        elif self.event_type == self.EventType.OFFLINE:
            if not (self.location or self.address):
                raise ValidationError("Offline events must have a location or address.")
        # HYBRID: both meeting_link and (location or address) are recommended but not strictly required
        # (you can add optional checks here)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    # ADDED: Concurrency-safe attendee registration
    def register_attendee(self):
        """Atomic increment of current_attendance if capacity allows."""
        if self.max_capacity is not None and self.current_attendance >= self.max_capacity:
            raise ValidationError("Event is full.")
        # Update atomically, then refresh the instance
        updated = self.__class__.objects.filter(pk=self.pk).update(
            current_attendance=F('current_attendance') + 1
        )
        if updated:
            self.refresh_from_db()
        else:
            raise ValidationError("Registration failed due to concurrent modification.")
        return self.current_attendance

    # ADDED: Atomic decrement (e.g., cancellation)
    def unregister_attendee(self):
        if self.current_attendance <= 0:
            raise ValidationError("No attendees to remove.")
        updated = self.__class__.objects.filter(pk=self.pk, current_attendance__gt=0).update(
            current_attendance=F('current_attendance') - 1
        )
        if updated:
            self.refresh_from_db()
        return self.current_attendance

    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at"])

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('event_detail', kwargs={'pk': self.pk})
    
class Registration(models.Model):
    class RegistrationStatus(models.TextChoices):
        PENDING = "P", "Pending"
        CONFIRMED = "C", "Confirmed"
        CANCELLED = "X", "Cancelled"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='registrations')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='participants')
    status = models.CharField(max_length=1, choices=RegistrationStatus.choices, default=RegistrationStatus.PENDING, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'event'],
                name='unique_user_event_registration'
            )
        ]

        indexes = [
            models.Index(fields=['user', 'event']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.user.email} -> {self.event.title}"

class EventLike(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='liked_events'
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='likes'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'event'],
                name='unique_event_like'
            )
        ]

class EventComment(models.Model):
    comment = models.TextField()
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='commented_events'
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    
    create_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)