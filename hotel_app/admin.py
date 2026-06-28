from django.contrib import admin
from hotel_app.models import (
    Hotel,
    DireccionHotel,
    TipoHabitacion,
    Habitacion,
    Cama,
    TipoHabitacionCama,
    ImagenHabitacion,
    Servicio,
)


admin.site.register(Hotel)
admin.site.register(DireccionHotel)
admin.site.register(TipoHabitacion)
admin.site.register(Habitacion)
admin.site.register(Cama)
admin.site.register(TipoHabitacionCama)
admin.site.register(ImagenHabitacion)
admin.site.register(Servicio)

from hotel_app.models.tipo_habitacion_servicio import TipoHabitacionServicio
from hotel_app.models.temporada import Temporada
from hotel_app.models.tarifa_habitacion import TarifaHabitacion
from hotel_app.models.reserva import Reserva
from hotel_app.models.reserva_habitacion import ReservaHabitacion
from hotel_app.models.huesped_reserva import HuespedReserva
from hotel_app.models.pago import Pago
from hotel_app.models.factura import Factura


admin.site.register(TipoHabitacionServicio)
admin.site.register(Temporada)
admin.site.register(TarifaHabitacion)
admin.site.register(Reserva)
admin.site.register(ReservaHabitacion)
admin.site.register(HuespedReserva)
admin.site.register(Pago)
admin.site.register(Factura)

from hotel_app.models import (
    PerfilUsuario,
    Cliente,
    DireccionCliente,
    DocumentoCliente,
    CargoEmpleado,
    Turno,
    Empleado,
    EmpleadoTurno
)

admin.site.register(PerfilUsuario)

admin.site.register(Cliente)
admin.site.register(DireccionCliente)
admin.site.register(DocumentoCliente)

admin.site.register(CargoEmpleado)
admin.site.register(Turno)
admin.site.register(Empleado)
admin.site.register(EmpleadoTurno)


