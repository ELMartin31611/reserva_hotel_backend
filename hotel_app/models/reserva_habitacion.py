from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator


class ReservaHabitacion(models.Model):
    ESTADO_CHOICES = [
        ('activa', 'Activa'),
        ('cancelada', 'Cancelada'),
        ('finalizada', 'Finalizada'),
    ]

    reserva = models.ForeignKey(
        'hotel_app.Reserva',
        on_delete=models.CASCADE,
        related_name='habitaciones_reservadas'
    )
    habitacion = models.ForeignKey(
        'hotel_app.Habitacion',
        on_delete=models.PROTECT,
        related_name='reservas_habitacion'
    )
    tarifa = models.ForeignKey(
        'hotel_app.TarifaHabitacion',
        on_delete=models.PROTECT,
        related_name='reservas_habitacion'
    )
    precio_noche = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    noches = models.PositiveIntegerField()
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    estado = models.CharField(
        max_length=30,
        choices=ESTADO_CHOICES,
        default='activa'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Habitación reservada'
        verbose_name_plural = 'Habitaciones reservadas'
        unique_together = ('reserva', 'habitacion')
        ordering = ['id']

    def clean(self):
        existe_cruce = ReservaHabitacion.objects.filter(
            habitacion=self.habitacion,
            reserva__estado__in=['pendiente', 'confirmada'],
            reserva__fecha_entrada__lt=self.reserva.fecha_salida,
            reserva__fecha_salida__gt=self.reserva.fecha_entrada,
        ).exclude(id=self.id).exists()

        if existe_cruce:
            raise ValidationError(
                'La habitación ya está reservada en ese rango de fechas.'
            )

    def save(self, *args, **kwargs):
        if self.tarifa and not self.precio_noche:
            self.precio_noche = self.tarifa.precio_noche

        if self.reserva:
            self.noches = self.reserva.numero_noches

        if self.precio_noche and self.noches:
            self.subtotal = self.precio_noche * self.noches

        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.reserva.codigo} - {self.habitacion}'