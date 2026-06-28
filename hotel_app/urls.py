from django.urls import path, include
from rest_framework.routers import DefaultRouter

from hotel_app.views.health import health_check
from hotel_app.views.pago import PagoViewSet

from hotel_app.views.factura import FacturaViewSet

router = DefaultRouter()
router.register(r'pagos', PagoViewSet, basename='pagos')

router.register(r'facturas', FacturaViewSet, basename='facturas')

urlpatterns = [
    path('health/', health_check, name='health-check'),
    path('', include(router.urls)),
]