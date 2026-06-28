
from .reserva import ReservaViewSet
from .reserva_habitacion import ReservaHabitacionViewSet
from .huesped_reserva import HuespedReservaViewSet
from .tipo_habitacion_servicio import TipoHabitacionServicioViewSet
from .temporada import TemporadaViewSet
from .tarifa_habitacion import TarifaHabitacionViewSet

from .perfil_usuario import (
    RegistroView,
    PerfilView
)

from .cliente import ClienteViewSet
from .direccion_cliente import DireccionClienteViewSet
from .documento_cliente import DocumentoClienteViewSet


from .cargo_empleado import (
    CargoEmpleadoViewSet
)

from .turno import TurnoViewSet
from .empleado import EmpleadoViewSet
from .empleado_turno import EmpleadoTurnoViewSet

