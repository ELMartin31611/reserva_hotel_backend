from django.db import models
from django.core.validators import MinValueValidator


class TipoHabitacionServicio(models.Model):
    tipo_habitacion = models.ForeignKey(
        'hotel_app.TipoHabitacion',
        on_delete=models.CASCADE,
        related_name='servicios_habitacion'
    )
    servicio = models.ForeignKey(
        'hotel_app.Servicio',
        on_delete=models.CASCADE,
        related_name='tipos_habitacion'
    )
    incluido = models.BooleanField(default=True)
    precio_personalizado = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Servicio por tipo de habitación'
        verbose_name_plural = 'Servicios por tipo de habitación'
        unique_together = ('tipo_habitacion', 'servicio')
        ordering = ['id']

    def __str__(self):
        return f'{self.tipo_habitacion} - {self.servicio}'