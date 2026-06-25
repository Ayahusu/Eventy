from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('events', views.EventViewset, basename='events')

urlpatterns = [
    path('', include(router.urls))
]