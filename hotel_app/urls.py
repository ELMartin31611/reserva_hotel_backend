from django.urls import path, include
from rest_framework.routers import DefaultRouter

from hotel_app.views.health import health_check
from hotel_app.views.reserva import ReservaViewSet



router = DefaultRouter()

router.register(r'reservas', ReservaViewSet, basename='reservas')

urlpatterns = [
    path('health/', health_check, name='health-check'),
    path('', include(router.urls)),
]