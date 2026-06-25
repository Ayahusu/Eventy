from django.db import transaction

from rest_framework.exceptions import ValidationError

from users.selectors.user_selector import UserSelector

class UserService:

    ALLOWED_FIELDS = {
        "bio",
        "country",
        "school_college",
        "profile_picture",
    }

    @staticmethod
    @transaction.atomic
    def delet_profile(user_id):
        user = UserSelector.get_user_by_id(user_id)

        if not user:
            raise ValidationError("User not Found")
        
        user.soft_delete()
        
        return {
            "message": "User deleted successfully"
        }

    @staticmethod
    @transaction.atomic
    def update_profile(user_id, data):
        user = UserSelector.get_user_by_id(user_id)
        
        if not user:
            raise ValidationError("User Not Found")
        
        updated_fields = []
        
        for field, value in data.items():

            if field not in UserService.ALLOWED_FIELDS:
                continue

            setattr(user, field, value)
            updated_fields.append(field)
        
        if updated_fields:
            user.save(
                update_fields=updated_fields
            )

        return user


    @staticmethod
    @transaction.atomic
    def change_password(
        user_id,
        old_password,
        new_password
    ):
        user = UserSelector.get_user_by_id(user_id)

        if not user:
            raise ValidationError("User not found")

        if not user.check_password(old_password):
            raise ValidationError(
                "Current password is incorrect"
            )

        user.set_password(new_password)
        user.save(update_fields=["password"])

        return user