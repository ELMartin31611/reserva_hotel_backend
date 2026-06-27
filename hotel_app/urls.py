from django.urls import path, include
from rest_framework.routers import DefaultRouter

from hotel_app.views.health import health_check
from hotel_app.views.tipo_habitacion_servicio import TipoHabitacionServicioViewSet


router = DefaultRouter()

router.register(
    r'tipos-habitacion-servicios',
    TipoHabitacionServicioViewSet,
    basename='tipos-habitacion-servicios'
)

urlpatterns = [
    path('health/', health_check, name='health-check'),
    path('', include(router.urls)),
]