from django.contrib import admin

from hotel_app.models import (
    PerfilUsuario,
    Cliente,
    DireccionCliente,
    DocumentoCliente,
    CargoEmpleado,
    Empleado,
    Turno,
    EmpleadoTurno,
    Hotel,
    DireccionHotel,
    TipoHabitacion,
    Habitacion,
    Cama,
    TipoHabitacionCama,
    ImagenHabitacion,
    Servicio,
)

from hotel_app.models.tipo_habitacion_servicio import TipoHabitacionServicio
from hotel_app.models.temporada import Temporada
from hotel_app.models.tarifa_habitacion import TarifaHabitacion
from hotel_app.models.reserva import Reserva
from hotel_app.models.reserva_habitacion import ReservaHabitacion
from hotel_app.models.huesped_reserva import HuespedReserva
from hotel_app.models.pago import Pago
from hotel_app.models.factura import Factura
from hotel_app.models.notificacion_sistema import NotificacionSistema


admin.site.register([
    PerfilUsuario,
    Cliente,
    DireccionCliente,
    DocumentoCliente,
    CargoEmpleado,
    Empleado,
    Turno,
    EmpleadoTurno,
    Hotel,
    DireccionHotel,
    TipoHabitacion,
    Habitacion,
    Cama,
    TipoHabitacionCama,
    ImagenHabitacion,
    Servicio,
    TipoHabitacionServicio,
    Temporada,
    TarifaHabitacion,
    Reserva,
    ReservaHabitacion,
    HuespedReserva,
    Pago,
    Factura,
])


@admin.register(NotificacionSistema)
class NotificacionSistemaAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'titulo',
        'tipo',
        'fecha_inicio',
        'fecha_fin',
        'is_active',
        'created_at',
    )

    list_filter = (
        'tipo',
        'is_active',
        'fecha_inicio',
    )

    search_fields = (
        'titulo',
        'mensaje',
    )

    ordering = (
        '-created_at',
    )