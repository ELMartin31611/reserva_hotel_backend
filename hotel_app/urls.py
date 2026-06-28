from django.urls import path, include
from rest_framework.routers import DefaultRouter

from hotel_app.views.health import health_check
from hotel_app.views.pago import PagoViewSet


router = DefaultRouter()
router.register(r'pagos', PagoViewSet, basename='pagos')


urlpatterns = [
    path('health/', health_check, name='health-check'),
    path('', include(router.urls)),
]