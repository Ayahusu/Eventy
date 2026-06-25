from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.validators import RegexValidator
import uuid

class Role(models.TextChoices):
    ATTENDEE = "ATTENDEE", "Attendee"
    ORGANISER = "ORGANISER", "Organiser"
    ADMIN = "ADMIN", "Admin"

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', Role.ADMIN)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)
    
    def get_queryset(self):
        return super().get_queryset().filter(
            deleted_at__isnull = True
        )

class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, db_index=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.ATTENDEE)
    
    # Profile fields
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)
    bio = models.TextField(blank=True)
    school_college = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=100, blank=True)
    
    # Status flags
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)       # For soft delete / ban
    is_staff = models.BooleanField(default=False)       # For admin site access
    is_superuser = models.BooleanField(default=False)   # Full permissions
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(
    null=True,
    blank=True
    )

    objects = UserManager()
    all_objects = models.Manager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
        ]
        constraints = [
        models.CheckConstraint(
            condition=models.Q(deleted_at__isnull=True) |
                     models.Q(is_active=False),
            name="deleted_user_inactive"
        )
        ]

    def soft_delete(self):

        self.deleted_at = timezone.now()
        self.is_active = False

        self.save(
            update_fields=[
                "deleted_at",
                "is_active",
                "updated_at"
            ]
        )

    def restore(self):
        self.deleted_at = None
        self.is_active = True

        self.save(
            update_fields=[
                "deleted_at",
                "is_active",
                "updated_at"
            ]
        )