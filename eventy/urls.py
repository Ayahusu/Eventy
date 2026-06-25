from django.contrib import admin
from django.urls import path, include

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from oauth2_provider import urls as oauth2_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('o/', include(oauth2_urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path(
    'v1/api/payments/',
    include('payments.api.urls')
),
path(
    'v1/api/',
    include('users.api.urls')
)
]
