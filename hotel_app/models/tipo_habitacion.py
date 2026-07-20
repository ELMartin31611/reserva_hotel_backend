from django.db import models

from hotel_app.models.hotel import Hotel


class TipoHabitacion(models.Model):
    hotel = models.ForeignKey(
        Hotel,
        on_delete=models.CASCADE,
        related_name='tipos_habitacion',
    )
    nombre = models.CharField(max_length=80)
    descripcion = models.TextField()
    capacidad_adultos = models.IntegerField()
    capacidad_ninos = models.IntegerField()
    capacidad_total = models.IntegerField()

    capacidad_extra = models.PositiveIntegerField(
        default=0,
        help_text=(
            'Cantidad máxima de huéspedes adicionales '
            'permitidos con recargo.'
        ),
    )

    tamano_m2 = models.DecimalField(
        max_digits=6,
        decimal_places=2,
    )
    precio_base = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
    estado = models.CharField(max_length=20)
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        db_table = 'tipo_habitacion'
        verbose_name = 'Tipo de Habitación'
        verbose_name_plural = 'Tipos de Habitación'

    @property
    def capacidad_maxima(self):
        return (
            self.capacidad_total
            + self.capacidad_extra
        )

    def __str__(self):
        return self.nombre