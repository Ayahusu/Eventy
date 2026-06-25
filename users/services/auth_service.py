from django.contrib.auth import authenticate
from django.db import transaction

from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import ValidationError


from users.models import User

class AuthService:

    @staticmethod
    @transaction.atomic
    def register_service(data):

        email = data.get("email")
        password = data.get("password")

        if not email:
            raise ValidationError({"email": "Email is required"})

        if not password:
            raise ValidationError({"password": "Password is required"})

        email = email.lower().strip()

        if User.objects.filter(email=email).exists():
            raise ValidationError({"email": "Email already exists"})

        user = User(email=email)
        user.set_password(password)
        user.save()

        return {
            "id": user.id,
            "email": user.email,
        }
    
    @staticmethod
    @transaction.atomic
    def login_service(data):

        email = data.get("email")
        password = data.get("password")

        if not email:
            raise AuthenticationFailed({
                "email": "Email is required"
            })

        if not password:
            raise AuthenticationFailed({
                "password": "Password is required"
            })

        authenticated_user = authenticate(
            username=email,
            password=password
        )

        if authenticated_user is None:
            raise AuthenticationFailed({
                "detail": "Invalid email or password"
            })

        if not authenticated_user.is_active:
            raise AuthenticationFailed({
                "detail": "Account is disabled"
            })

        refresh = RefreshToken.for_user(authenticated_user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": authenticated_user.id,
                "email": authenticated_user.email,
            }
        }
    