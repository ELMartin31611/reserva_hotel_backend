from django.contrib import admin

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