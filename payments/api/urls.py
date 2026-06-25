from rest_framework.routers import DefaultRouter

from payments.api.views import PaymentViewSet

router = DefaultRouter()
router.register(
    '',
    PaymentViewSet,
    basename='payments'
)

urlpatterns = router.urls