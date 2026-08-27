from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from ..models import User, Role
import uuid

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'email', 'role', 'profile_picture', 'bio',
            'school_college', 'country', 'is_verified', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'is_verified', 'created_at', 'updated_at')

    def update(self, instance, validated_data):
        # Prevent role escalation via normal update (optional security)
        if 'role' in validated_data and validated_data['role'] != instance.role:
            # Only allow if user is admin? This check belongs in the view/permissions.
            # For safety, we remove role from update unless explicitly allowed.
            validated_data.pop('role')
        return super().update(instance, validated_data)

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = (
            'email', 'password', 'password_confirm', 'role', 'profile_picture',
            'bio', 'school_college', 'country'
        )
        extra_kwargs = {
            'email': {'required': True},
            'role': {'required': False},  # default is Attendee
        }

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value.lower()

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Password fields do not match."})
        return data

    def create(self, validated_data):
        # Remove password_confirm before creating user
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'profile_picture', 'bio', 'school_college', 'country'
        )

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password_confirm": "New passwords do not match."})
        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value