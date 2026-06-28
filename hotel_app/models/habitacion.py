from django.db import models

from hotel_app.models.hotel import Hotel
from hotel_app.models.tipo_habitacion import TipoHabitacion


class Habitacion(models.Model):
    hotel = models.ForeignKey(
        Hotel,
        on_delete=models.CASCADE,
        related_name="habitaciones"
    )

    tipo_habitacion = models.ForeignKey(
        TipoHabitacion,
        on_delete=models.CASCADE,
        related_name="habitaciones"
    )

    numero = models.CharField(max_length=20)
    piso = models.IntegerField()
    estado = models.CharField(max_length=30)
    descripcion = models.TextField()
    es_fumador = models.BooleanField(default=False)
    observaciones = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "habitacion"
        verbose_name = "Habitación"
        verbose_name_plural = "Habitaciones"

    def __str__(self):
        return f"Habitación {self.numero}"