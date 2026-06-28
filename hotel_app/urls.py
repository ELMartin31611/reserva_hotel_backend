from django.urls import path, include
from rest_framework.routers import DefaultRouter

from hotel_app.views.health import health_check
from hotel_app.views.reserva import ReservaViewSet
from hotel_app.views.reserva_habitacion import ReservaHabitacionViewSet
from hotel_app.views.huesped_reserva import HuespedReservaViewSet


router = DefaultRouter()

router.register(r'reservas', ReservaViewSet, basename='reservas')
router.register(
    r'reserva-habitaciones',
    ReservaHabitacionViewSet,
    basename='reserva-habitaciones'
)
router.register(
    r'huespedes-reserva',
    HuespedReservaViewSet,
    basename='huespedes-reserva'
)


urlpatterns = [
    path('health/', health_check, name='health-check'),
    path('', include(router.urls)),
]