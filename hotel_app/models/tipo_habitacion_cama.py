from django.db import models

from hotel_app.models.tipo_habitacion import TipoHabitacion
from hotel_app.models.cama import Cama


class TipoHabitacionCama(models.Model):
    tipo_habitacion = models.ForeignKey(
        TipoHabitacion,
        on_delete=models.CASCADE,
        related_name="camas"
    )

    cama = models.ForeignKey(
        Cama,
        on_delete=models.CASCADE,
        related_name="tipos_habitacion"
    )

    cantidad = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tipo_habitacion_cama"
        verbose_name = "Cama por Tipo de Habitación"
        verbose_name_plural = "Camas por Tipo de Habitación"

    def __str__(self):
        return f"{self.tipo_habitacion.nombre} - {self.cama.nombre} x{self.cantidad}"