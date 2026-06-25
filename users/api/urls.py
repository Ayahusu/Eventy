from rest_framework.routers import DefaultRouter

from users.api.auth_views import UserAuthViewSet
from users.api.user_views import UserViewSet

router = DefaultRouter()

router.register(
    r"auth",
    UserAuthViewSet,
    basename="auth"
)

router.register(
    r"users",
    UserViewSet,
    basename="users"
)

urlpatterns = [*router.urls]