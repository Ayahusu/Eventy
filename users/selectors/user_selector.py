from users.models import User

class UserSelector:

    @staticmethod
    def get_user_by_id(user_id):
        return User.objects.filter(
            pk=user_id
        ).first()

    @staticmethod
    def get_user_by_email(email):
        return User.objects.filter(
            email=email
        ).first()