from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from hotel_app.views.health import health_check
from hotel_app.views import (
    RegistroView,
    PerfilView,
    PerfilUsuarioViewSet,
    ClienteViewSet,
    DireccionClienteViewSet,
    DocumentoClienteViewSet,
    CargoEmpleadoViewSet,
    TurnoViewSet,
    EmpleadoViewSet,
    EmpleadoTurnoViewSet,
    HotelViewSet,
    DireccionHotelViewSet,
    TipoHabitacionViewSet,
    HabitacionViewSet,
    CamaViewSet,
    TipoHabitacionCamaViewSet,
    ImagenHabitacionViewSet,
    ServicioViewSet,
    TipoHabitacionServicioViewSet,
    TemporadaViewSet,
    TarifaHabitacionViewSet,
    ReservaViewSet,
    ReservaHabitacionViewSet,
    HuespedReservaViewSet,
    PagoViewSet,
    FacturaViewSet,
    NotificacionSistemaViewSet,
)

router = DefaultRouter()

# 01 PerfilUsuario
router.register(r'perfiles', PerfilUsuarioViewSet, basename='perfiles')

# 02 - 04 Clientes
router.register(r'clientes', ClienteViewSet, basename='clientes')
router.register(r'direcciones', DireccionClienteViewSet, basename='direcciones')
router.register(r'documentos', DocumentoClienteViewSet, basename='documentos')

# 05 - 08 Empleados
router.register(r'cargos', CargoEmpleadoViewSet, basename='cargos')
router.register(r'empleados', EmpleadoViewSet, basename='empleados')
router.register(r'turnos', TurnoViewSet, basename='turnos')
router.register(r'empleado-turnos', EmpleadoTurnoViewSet, basename='empleado-turnos')

# 09 - 16 Hotel y habitaciones
router.register(r'hoteles', HotelViewSet, basename='hoteles')
router.register(r'direcciones-hotel', DireccionHotelViewSet, basename='direcciones-hotel')
router.register(r'tipos-habitacion', TipoHabitacionViewSet, basename='tipos-habitacion')
router.register(r'habitaciones', HabitacionViewSet, basename='habitaciones')
router.register(r'camas', CamaViewSet, basename='camas')
router.register(r'tipos-habitacion-camas', TipoHabitacionCamaViewSet, basename='tipos-habitacion-camas')
router.register(r'imagenes-habitacion', ImagenHabitacionViewSet, basename='imagenes-habitacion')
router.register(r'servicios', ServicioViewSet, basename='servicios')

# 17 - 19 Servicios y tarifas
router.register(r'tipos-habitacion-servicios', TipoHabitacionServicioViewSet, basename='tipos-habitacion-servicios')
router.register(r'temporadas', TemporadaViewSet, basename='temporadas')
router.register(r'tarifas-habitacion', TarifaHabitacionViewSet, basename='tarifas-habitacion')

# 20 - 24 Reservas y facturación
router.register(r'reservas', ReservaViewSet, basename='reservas')
router.register(r'reserva-habitaciones', ReservaHabitacionViewSet, basename='reserva-habitaciones')
router.register(r'huespedes-reserva', HuespedReservaViewSet, basename='huespedes-reserva')
router.register(r'pagos', PagoViewSet, basename='pagos')
router.register(r'facturas', FacturaViewSet, basename='facturas')

# 25 Sistema
router.register(r'notificaciones-sistema', NotificacionSistemaViewSet, basename='notificaciones-sistema')

urlpatterns = [
    path('health/', health_check, name='health-check'),
    path('register/', RegistroView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('perfil/', PerfilView.as_view(), name='perfil'),
    path('', include(router.urls)),
]
