from django.urls import include, path
from rest_framework.routers import DefaultRouter

from hotel_app.views import (
    HotelViewSet,
    DireccionHotelViewSet,
    TipoHabitacionViewSet,
    HabitacionViewSet,
    CamaViewSet,
    TipoHabitacionCamaViewSet,
    ImagenHabitacionViewSet,
    ServicioViewSet,
)

router = DefaultRouter()

router.register(
    r"hoteles",
    HotelViewSet,
    basename="hotel"
)

router.register(
    r"direcciones-hotel",
    DireccionHotelViewSet,
    basename="direccion-hotel"
)

router.register(
    r"tipos-habitacion",
    TipoHabitacionViewSet,
    basename="tipo-habitacion"
)

router.register(
    r"habitaciones",
    HabitacionViewSet,
    basename="habitacion"
)

router.register(
    r"camas",
    CamaViewSet,
    basename="cama"
)

router.register(
    r"tipos-habitacion-camas",
    TipoHabitacionCamaViewSet,
    basename="tipo-habitacion-cama"
)

router.register(
    r"imagenes-habitacion",
    ImagenHabitacionViewSet,
    basename="imagen-habitacion"
)

router.register(
    r"servicios",
    ServicioViewSet,
    basename="servicio"
)

urlpatterns = [
    path("", include(router.urls)),
]