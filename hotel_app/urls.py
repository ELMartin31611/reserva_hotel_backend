from django.urls import path, include
from rest_framework.routers import DefaultRouter

from hotel_app.views.health import health_check
from hotel_app.views.tipo_habitacion_servicio import TipoHabitacionServicioViewSet
from hotel_app.views.temporada import TemporadaViewSet
from hotel_app.views.tarifa_habitacion import TarifaHabitacionViewSet


router = DefaultRouter()

router.register(
    r'tipos-habitacion-servicios',
    TipoHabitacionServicioViewSet,
    basename='tipos-habitacion-servicios'
)

router.register(r'temporadas', TemporadaViewSet, basename='temporadas')

router.register(
    r'tarifas-habitacion',
    TarifaHabitacionViewSet,
    basename='tarifas-habitacion'
)

urlpatterns = [
    path('health/', health_check, name='health-check'),
    path('', include(router.urls)),
]