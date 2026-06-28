from django.db import models
from django.core.validators import MinValueValidator


class TarifaHabitacion(models.Model):
    tipo_habitacion = models.ForeignKey(
        'hotel_app.TipoHabitacion',
        on_delete=models.CASCADE,
        related_name='tarifas'
    )
    temporada = models.ForeignKey(
        'hotel_app.Temporada',
        on_delete=models.CASCADE,
        related_name='tarifas'
    )
    precio_noche = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    precio_fin_semana = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    precio_persona_extra = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    moneda = models.CharField(max_length=10, default='USD')
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Tarifa de habitación'
        verbose_name_plural = 'Tarifas de habitación'
        unique_together = ('tipo_habitacion', 'temporada')
        ordering = ['id']

    def __str__(self):
        return f'{self.tipo_habitacion} - {self.temporada} - {self.precio_noche}'