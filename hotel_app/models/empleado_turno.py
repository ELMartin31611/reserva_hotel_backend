from django.db import models

from .empleado import Empleado
from .turno import Turno


class EmpleadoTurno(models.Model):

    empleado = models.ForeignKey(
        Empleado,
        on_delete=models.CASCADE,
        related_name='turnos_asignados'
    )

    turno = models.ForeignKey(
        Turno,
        on_delete=models.CASCADE,
        related_name='empleados_asignados'
    )

    dia_semana = models.CharField(
        max_length=20
    )

    fecha_inicio = models.DateField()

    fecha_fin = models.DateField(
        blank=True,
        null=True
    )

    activo = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.empleado} - {self.turno}"

    class Meta:
        db_table = 'empleado_turno'