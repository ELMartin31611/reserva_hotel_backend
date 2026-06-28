from django.urls import path
from rest_framework.routers import DefaultRouter
from hotel_app.views.health import health_check
from hotel_app.views.reserva import ReservaViewSet
from hotel_app.views.reserva_habitacion import ReservaHabitacionViewSet
from hotel_app.views.huesped_reserva import HuespedReservaViewSet
from hotel_app.views.tipo_habitacion_servicio import TipoHabitacionServicioViewSet
from hotel_app.views.temporada import TemporadaViewSet
from hotel_app.views.tarifa_habitacion import TarifaHabitacionViewSet


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

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)

from hotel_app.views import (
    RegistroView,
    PerfilView,

    ClienteViewSet,
    DireccionClienteViewSet,
    DocumentoClienteViewSet,

    CargoEmpleadoViewSet,
    TurnoViewSet,
    EmpleadoViewSet,
    EmpleadoTurnoViewSet
)

router = DefaultRouter()


router.register(
    'clientes',
    ClienteViewSet
)

router.register(
    'direcciones',
    DireccionClienteViewSet
)

router.register(
    'documentos',
    DocumentoClienteViewSet
)



router.register(
    'cargos',
    CargoEmpleadoViewSet
)

router.register(
    'turnos',
    TurnoViewSet
)

router.register(
    'empleados',
    EmpleadoViewSet
)

router.register(
    'empleado-turnos',
    EmpleadoTurnoViewSet

)


urlpatterns = [

    path(
        'register/',
        RegistroView.as_view(),
        name='register'
    ),

    path(
        'login/',
        TokenObtainPairView.as_view(),
        name='login'
    ),

    path(
        'token/refresh/',
        TokenRefreshView.as_view(),
        name='token_refresh'
    ),

    path(
        'perfil/',
        PerfilView.as_view(),
        name='perfil'
    ),

]

urlpatterns += router.urls