from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from drf_spectacular.utils import extend_schema

urlpatterns = [
    path('admin/', admin.site.urls),
    path('v1/api/auth/token/', extend_schema(tags=['Auth API Endpoint'])(TokenObtainPairView).as_view(), name='token_obtain_pair'),
    path('v1/api/auth/token/refresh/',extend_schema(tags=['Auth API Endpoint'])(TokenRefreshView).as_view(), name='token_refresh'),
    path('', include('django_prometheus.urls')),
    path(
        'v1/api/events/',
        include('event.api.urls')
    ),
    path(
        'v1/api/',
        include('users.api.urls')
    ),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Optional UI:
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)